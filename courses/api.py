"""API for the Courses app"""

import itertools
import logging
from collections import namedtuple
from datetime import datetime, timedelta
from traceback import format_exc
from typing import Optional, List

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from mitol.common.utils import now_in_utc
from mitol.common.utils.collections import (
    first_or_none,
    has_equal_properties,
    partition,
)
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError
from openedx.api import get_edx_grades_with_users
from openedx.constants import EDX_DEFAULT_ENROLLMENT_MODE
from rest_framework.status import HTTP_404_NOT_FOUND

from courses import mail_api
from courses.constants import ENROLL_CHANGE_STATUS_DEFERRED, PROGRAM_TEXT_ID_PREFIX
from courses.models import (
    CourseRun,
    CourseRunEnrollment,
    CourseRunGrade,
    CourseRunCertificate,
    Program,
    ProgramEnrollment,
    Course,
)
from courses.tasks import subscribe_edx_course_emails
from courses.utils import exception_logging_generator, is_grade_valid
from openedx.api import (
    enroll_in_edx_course_runs,
    get_edx_api_course_detail_client,
    get_edx_api_course_mode_client,
    unenroll_edx_course_run,
)
from openedx.exceptions import (
    EdxApiEnrollErrorException,
    NoEdxApiAuthError,
    UnknownEdxApiEnrollException,
)
from openedx.constants import EDX_ENROLLMENT_VERIFIED_MODE
from users.models import User

log = logging.getLogger(__name__)
UserEnrollments = namedtuple(
    "UserEnrollments",
    [
        "programs",
        "past_programs",
        "program_runs",
        "non_program_runs",
        "past_non_program_runs",
    ],
)


def get_user_relevant_course_run_qset(
    course: Course, user: Optional[User], now: Optional[datetime] = None
) -> QuerySet:
    """
    Returns a QuerySet of relevant course runs
    """
    now = now or now_in_utc()
    run_qset = (
        course.courseruns.exclude(start_date=None)
        .exclude(enrollment_start=None)
        .filter(Q(end_date=None) | Q(end_date__gt=now))
    )
    if user and user.is_authenticated:
        user_enrollments = Count(
            "enrollments",
            filter=Q(
                enrollments__user=user,
                enrollments__active=True,
                enrollments__edx_enrolled=True,
            ),
        )
        run_qset = run_qset.annotate(user_enrollments=user_enrollments).order_by(
            "-user_enrollments", "enrollment_start"
        )

        verified_enrollments = Count(
            "enrollments",
            filter=Q(
                enrollments__user=user,
                enrollments__active=True,
                enrollments__edx_enrolled=True,
                enrollments__enrollment_mode=EDX_ENROLLMENT_VERIFIED_MODE,
            ),
        )
        run_qset = run_qset.annotate(verified_enrollments=verified_enrollments)

        runs = run_qset.filter(
            Q(user_enrollments__gt=0)
            | Q(enrollment_end=None)
            | Q(enrollment_end__gt=now)
        )
    else:
        runs = run_qset.filter(
            Q(enrollment_end=None) | Q(enrollment_end__gt=now)
        ).order_by("enrollment_start")
    return runs


def get_user_relevant_course_run(
    course: Course, user: Optional[User], now: Optional[datetime] = None
) -> CourseRun:
    """
    For a given Course, finds the course run that is the most relevant to the user.
    For anonymous users, this means the soonest enrollable course run.
    For logged-in users, this means an active course run that they're enrolled in, or the soonest enrollable course run.
    """
    runs = get_user_relevant_course_run_qset(course, user, now)
    run = first_or_none(runs)
    return run


def get_user_enrollments(user):
    """
    Fetches a user's enrollments

    If the user is enrolled in a course that belongs to a program, we count that
    as an enrollment in the program (and we create an ephemeral
    ProgramEnrollment for that) unless the user is already enrolled in the
    program directly.

    Args:
        user (User): A user
    Returns:
        UserEnrollments: An object representing a user's program and course run enrollments
    """
    course_run_enrollments = (
        CourseRunEnrollment.objects.filter(user=user).order_by("run__start_date").all()
    )

    all_course_run_programs = []  # all the programs that the course runs belong to
    filtered_course_run_programs = (
        []
    )  # just the programs we don't have distinct ProgramEnrollments for

    for program in [
        cre.run.course.program
        for cre in course_run_enrollments
        if cre.run.course.program is not None
    ]:
        if program not in all_course_run_programs:
            all_course_run_programs.append(program)

    program_enrollments = (
        ProgramEnrollment.objects.prefetch_related("program__courses")
        .select_related("user")
        .filter(user=user)
        .all()
    )

    for program in all_course_run_programs:
        found = False

        for enrollment in program_enrollments:
            if enrollment.program == program:
                found = True
                break

        if not found:
            filtered_course_run_programs.append(program)

    program_enrollments = list(
        itertools.chain(
            program_enrollments,
            [
                ProgramEnrollment(user=user, program=program)
                for program in filtered_course_run_programs
            ],
        )
    )

    program_courses = itertools.chain(
        *(
            program_enrollment.program.courses.all()
            for program_enrollment in program_enrollments
        )
    )
    program_course_ids = set(course.id for course in program_courses)
    non_program_run_enrollments, program_run_enrollments = partition(
        course_run_enrollments,
        lambda course_run_enrollment: (
            course_run_enrollment.run.course_id in program_course_ids
        ),
    )
    program_enrollments, past_program_enrollments = partition(
        program_enrollments, lambda program_enrollment: program_enrollment.is_ended
    )
    non_program_run_enrollments, past_non_program_run_enrollments = partition(
        non_program_run_enrollments,
        lambda non_program_run_enrollment: non_program_run_enrollment.is_ended,
    )

    return UserEnrollments(
        programs=program_enrollments,
        past_programs=past_program_enrollments,
        program_runs=program_run_enrollments,
        non_program_runs=non_program_run_enrollments,
        past_non_program_runs=past_non_program_run_enrollments,
    )


def create_run_enrollments(
    user, runs, *, keep_failed_enrollments=False, mode=EDX_DEFAULT_ENROLLMENT_MODE
):
    """
    Creates local records of a user's enrollment in course runs, and attempts to enroll them
    in edX via API

    Args:
        user (User): The user to enroll
        runs (iterable of CourseRun): The course runs to enroll in
        keep_failed_enrollments: (boolean): If True, keeps the local enrollment record
            in the database even if the enrollment fails in edX.

    Returns:
        (list of CourseRunEnrollment, bool): A list of enrollment objects that were successfully
            created, paired with a boolean indicating whether or not edX enrollment was successful
            for all of the given course runs
    """
    successful_enrollments = []

    def send_enrollment_emails():
        subscribe_edx_course_emails.delay(enrollment.id)

    try:
        enroll_in_edx_course_runs(user, runs, mode=mode)
    except (
        EdxApiEnrollErrorException,
        UnknownEdxApiEnrollException,
        NoEdxApiAuthError,
        HTTPError,
        RequestsConnectionError,
    ):
        log.exception(
            "edX enrollment failure for user: %s, runs: %s",
            user,
            [run.courseware_id for run in runs],
        )
        edx_request_success = False
        if not keep_failed_enrollments:
            return successful_enrollments, edx_request_success
    else:
        edx_request_success = True

    for run in runs:
        try:
            enrollment, created = CourseRunEnrollment.all_objects.get_or_create(
                user=user,
                run=run,
                defaults=dict(edx_enrolled=edx_request_success, enrollment_mode=mode),
            )

            if run.course.program is not None:
                related_program = ProgramEnrollment.objects.get_or_create(
                    user=user, program=run.course.program
                )

            if not created:
                enrollment_mode_changed = mode != enrollment.enrollment_mode
                # Case (Upgrade): When user was enrolled in free mode and now enrolls in paid mode (e.g. Verified)
                # So, User has an active enrollment and the only changing thing is going to be enrollment mode
                if enrollment.active and enrollment_mode_changed:
                    enrollment.edx_enrolled = edx_request_success
                    enrollment.update_mode_and_save(mode=mode)

                elif not enrollment.active:
                    enrollment.edx_enrolled = edx_request_success
                    if enrollment_mode_changed:
                        enrollment.enrollment_mode = mode
                    enrollment.reactivate_and_save()
                    transaction.on_commit(send_enrollment_emails)
        except:  # pylint: disable=bare-except
            mail_api.send_enrollment_failure_message(user, run, details=format_exc())
            log.exception(
                "Failed to create/update enrollment record (user: %s, run: %s)",
                user,
                run.courseware_id,
            )
            pass
        else:
            successful_enrollments.append(enrollment)
            if enrollment.edx_enrolled:
                mail_api.send_course_run_enrollment_email(enrollment)
    return successful_enrollments, edx_request_success


def create_program_enrollments(user, programs):
    """
    Creates local records of a user's enrollment in programs

    Args:
        user (User): The user to enroll
        programs (iterable of Program): The course runs to enroll in

    Returns:
        list of ProgramEnrollment: A list of enrollment objects that were successfully created
    """
    successful_enrollments = []
    for program in programs:
        try:
            enrollment, created = ProgramEnrollment.all_objects.get_or_create(
                user=user,
                program=program,
            )
            if not created and not enrollment.active:
                enrollment.reactivate_and_save()
        except:  # pylint: disable=bare-except
            mail_api.send_enrollment_failure_message(
                user, program, details=format_exc()
            )
            log.exception(
                "Failed to create/update enrollment record (user: %s, program: %s)",
                user,
                program.readable_id,
            )
            pass
        else:
            successful_enrollments.append(enrollment)
    return successful_enrollments


def deactivate_run_enrollment(
    run_enrollment, change_status, keep_failed_enrollments=False
):
    """
    Helper method to deactivate a CourseRunEnrollment

    Args:
        run_enrollment (CourseRunEnrollment): The course run enrollment to deactivate
        change_status (str): The change status to set on the enrollment when deactivating
        keep_failed_enrollments: (boolean): If True, keeps the local enrollment record
            in the database even if the enrollment fails in edX.

    Returns:
        CourseRunEnrollment: The deactivated enrollment
    """
    try:
        unenroll_edx_course_run(run_enrollment)
    except Exception:  # pylint: disable=broad-except
        log.exception(
            "Failed to unenroll course run '%s' for user '%s' in edX",
            run_enrollment.run.courseware_id,
            run_enrollment.user.email,
        )
        if not keep_failed_enrollments:
            return None
        edx_unenrolled = False
    else:
        edx_unenrolled = True
        mail_api.send_course_run_unenrollment_email(run_enrollment)
    if edx_unenrolled:
        run_enrollment.edx_enrolled = False
        run_enrollment.edx_emails_subscription = False
    run_enrollment.deactivate_and_save(change_status, no_user=True)
    return run_enrollment


def deactivate_program_enrollment(
    program_enrollment,
    change_status,
    keep_failed_enrollments=False,
):
    """
    Helper method to deactivate a ProgramEnrollment

    Args:
        program_enrollment (ProgramEnrollment): The program enrollment to deactivate
        change_status (str): The change status to set on the enrollment when deactivating
        keep_failed_enrollments: (boolean): If True, keeps the local enrollment record
            in the database even if the enrollment fails in edX.

    Returns:
        tuple of ProgramEnrollment, list(CourseRunEnrollment): The deactivated enrollments
    """
    program_run_enrollments = program_enrollment.get_run_enrollments()

    deactivated_course_runs = []
    for run_enrollment in program_run_enrollments:
        if deactivate_run_enrollment(
            run_enrollment,
            change_status=change_status,
            keep_failed_enrollments=keep_failed_enrollments,
        ):
            deactivated_course_runs.append(run_enrollment)

    if deactivated_course_runs:
        program_enrollment.deactivate_and_save(change_status, no_user=True)
    else:
        return None, None

    return program_enrollment, deactivated_course_runs


def defer_enrollment(
    user,
    from_courseware_id,
    to_courseware_id,
    keep_failed_enrollments=False,
    force=False,
):
    """
    Deactivates a user's existing enrollment in one course run and enrolls the user in another.

    Args:
        user (User): The enrolled user
        from_courseware_id (str): The courseware_id value of the currently enrolled CourseRun
        to_courseware_id (str): The courseware_id value of the desired CourseRun
        keep_failed_enrollments: (boolean): If True, keeps the local enrollment record
            in the database even if the enrollment fails in edX.
        force (bool): If True, the deferral will be completed even if the current enrollment is inactive
            or the desired enrollment is in a different course

    Returns:
        (CourseRunEnrollment, CourseRunEnrollment): The deactivated enrollment paired with the
            new enrollment that was the target of the deferral
    """
    from_enrollment = CourseRunEnrollment.all_objects.get(
        user=user, run__courseware_id=from_courseware_id
    )
    if not force and not from_enrollment.active:
        raise ValidationError(
            "Cannot defer from inactive enrollment (id: {}, run: {}, user: {}). "
            "Set force=True to defer anyway.".format(
                from_enrollment.id, from_enrollment.run.courseware_id, user.email
            )
        )
    to_run = CourseRun.objects.get(courseware_id=to_courseware_id)
    if from_enrollment.run == to_run:
        raise ValidationError(
            "Cannot defer to the same course run (run: {})".format(to_run.courseware_id)
        )
    if not to_run.is_not_beyond_enrollment:
        raise ValidationError(
            "Cannot defer to a course run that is outside of its enrollment period (run: {}).".format(
                to_run.courseware_id
            )
        )
    if not force and from_enrollment.run.course != to_run.course:
        raise ValidationError(
            "Cannot defer to a course run of a different course ('{}' -> '{}'). "
            "Set force=True to defer anyway.".format(
                from_enrollment.run.course.title, to_run.course.title
            )
        )
    to_enrollments, _ = create_run_enrollments(
        user,
        [to_run],
        keep_failed_enrollments=keep_failed_enrollments,
    )
    from_enrollment = deactivate_run_enrollment(
        from_enrollment,
        ENROLL_CHANGE_STATUS_DEFERRED,
        keep_failed_enrollments=keep_failed_enrollments,
    )
    return from_enrollment, first_or_none(to_enrollments)


def ensure_course_run_grade(user, course_run, edx_grade, should_update=False):
    """
    Ensure that the local grades repository has the grade for the User/CourseRun combination supplied.

    Args:
        user (user.models.User): The user for whom the grade is being synced
        course_run (courses.models.CourseRun): The course run for which the grade is created
        edx_grade (edx_api.grades.models.UserCurrentGrade): The OpenEdx grade object
        should_update (bool): Update the local grade record if it exists

    Returns:
        Tuple[ CourseRunGrade, bool, bool ]: A Tuple containing None or CourseRunGrade object,
            A bool representing if the run grade is created, A bool representing if a run grade is updated
    """
    grade_properties = {
        "grade": edx_grade.percent,
        "passed": edx_grade.passed,
        "letter_grade": edx_grade.letter_grade,
    }

    updated = False
    if should_update:
        with transaction.atomic():
            (
                run_grade,
                created,
            ) = CourseRunGrade.objects.select_for_update().get_or_create(
                course_run=course_run, user=user, defaults=grade_properties
            )

            if (
                not created
                and not run_grade.set_by_admin
                and not has_equal_properties(run_grade, grade_properties)
            ):
                # Perform actual update now.
                run_grade.grade = edx_grade.percent
                run_grade.passed = edx_grade.passed
                run_grade.letter_grade = edx_grade.letter_grade
                run_grade.save_and_log(None)
                updated = True

    else:
        run_grade, created = CourseRunGrade.objects.get_or_create(
            course_run=course_run, user=user, defaults=grade_properties
        )
    return run_grade, created, updated


def sync_course_runs(runs):
    """
    Sync course run dates and title from Open edX

    Args:
        runs ([CourseRun]): list of CourseRun objects.

    Returns:
        [str], [str]: Lists of success and error logs respectively
    """
    api_client = get_edx_api_course_detail_client()

    success_count = 0
    failure_count = 0

    # Iterate all eligible runs and sync if possible
    for run in runs:
        try:
            course_detail = api_client.get_detail(
                course_id=run.courseware_id,
                username=settings.OPENEDX_SERVICE_WORKER_USERNAME,
            )
        except HTTPError as e:
            failure_count += 1
            if e.response.status_code == HTTP_404_NOT_FOUND:
                log.error(
                    "Course not found on edX for readable id: %s", run.courseware_id
                )
            else:
                log.error("%s: %s", str(e), run.courseware_id)
        except Exception as e:  # pylint: disable=broad-except
            failure_count += 1
            log.error("%s: %s", str(e), run.courseware_id)
        else:
            # Reset the expiration_date so it is calculated automatically and
            # does not raise a validation error now that the start or end date
            # has changed.
            if (
                run.start_date != course_detail.start
                or run.end_date != course_detail.end
            ):
                run.expiration_date = None

            run.title = course_detail.name
            run.start_date = course_detail.start
            run.end_date = course_detail.end
            run.enrollment_start = course_detail.enrollment_start
            run.enrollment_end = course_detail.enrollment_end
            try:
                run.save()
                success_count += 1
                log.info("Updated course run: %s", run.courseware_id)
            except Exception as e:  # pylint: disable=broad-except
                # Report any validation or otherwise model errors
                log.error("%s: %s", str(e), run.courseware_id)
                failure_count += 1

    return success_count, failure_count


def sync_course_mode(runs: List[CourseRun]) -> List[str]:
    """
    Updates course run upgrade expiration dates from Open edX

    Args:
        runs ([CourseRun]): list of CourseRun objects.

    Returns:
        [str], [str]: Lists of success and error logs respectively
    """
    api_client = get_edx_api_course_mode_client()

    success_count = 0
    failure_count = 0

    # Iterate all eligible runs and sync if possible
    for run in runs:
        try:
            course_modes = api_client.get_mode(
                course_id=run.courseware_id,
            )
        except HTTPError as e:
            failure_count += 1
            if e.response.status_code == HTTP_404_NOT_FOUND:
                log.error(
                    "Course mode not found on edX for readable id: %s",
                    run.courseware_id,
                )
            else:
                log.error("%s: %s", str(e), run.courseware_id)
        except Exception as e:  # pylint: disable=broad-except
            failure_count += 1
            log.error("%s: %s", str(e), run.courseware_id)
        else:
            for course_mode in course_modes:
                if (
                    course_mode.mode_slug == "verified"
                    and run.upgrade_deadline != course_mode.expiration_datetime
                ):
                    run.upgrade_deadline = course_mode.expiration_datetime
                    try:
                        run.save()
                        success_count += 1
                        log.info(
                            "Updated upgrade deadline for course run: %s",
                            run.courseware_id,
                        )
                    except Exception as e:  # pylint: disable=broad-except
                        # Report any validation or otherwise model errors
                        log.error("%s: %s", str(e), run.courseware_id)
                        failure_count += 1

    return success_count, failure_count


def is_program_text_id(item_text_id):
    """
    Analyzes a text id for some enrollable item and returns True if it's a program id

    Args:
        item_text_id (str): The text id for some enrollable item (program/course run)

    Returns:
        bool: True if the given id is a program id
    """
    return item_text_id.startswith(PROGRAM_TEXT_ID_PREFIX)


def process_course_run_grade_certificate(course_run_grade, should_force_create=False):
    """
    Ensure that the course run certificate is in line with the values in the course run grade

    Args:
        course_run_grade (courses.models.CourseRunGrade): The course run grade for which to generate/delete the certificate
        should_force_create (bool): If True, it will force the certificate creation without matching criteria
    Returns:
        Tuple[ CourseRunCertificate, bool, bool ]: A Tuple containing None or CourseRunCertificate object,
            A bool representing if the certificate is created, A bool representing if a certificate is deleted
    """
    user = course_run_grade.user
    course_run = course_run_grade.course_run

    # A grade of 0.0 indicates that the certificate should be deleted
    should_delete = not bool(course_run_grade.grade)
    should_create = course_run_grade.is_certificate_eligible or should_force_create

    if should_delete:
        delete_count, _ = CourseRunCertificate.objects.filter(
            user=user, course_run=course_run
        ).delete()
        return None, False, (delete_count > 0)

    elif should_create:
        certificate, created = CourseRunCertificate.objects.get_or_create(
            user=user, course_run=course_run
        )
        return certificate, created, False
    return None, False, False


def get_certificate_grade_eligible_runs(now):
    """
    Get the list of course runs that are eligible for Grades update/creation and certificates creation
    """
    # Get all the course runs valid course runs for certificates/Grades
    # For a valid run it would be live,
    # .. end_date would be in future with addition of delay settings.CERTIFICATE_CREATION_DELAY_IN_HOURS

    course_runs = CourseRun.objects.live().filter(
        Q(end_date__isnull=True)
        | Q(
            end_date__gt=now
            - timedelta(hours=settings.CERTIFICATE_CREATION_DELAY_IN_HOURS)
        )
    )
    return course_runs


def generate_course_run_certificates():
    """
    Hits the edX grades API for eligible course runs and generates the certificates and grades for users for course runs
    """
    now = now_in_utc()
    course_runs = get_certificate_grade_eligible_runs(now)

    if course_runs is None or course_runs.count() == 0:
        log.info("No course runs matched the certificates generation criteria")
        return

    for run in course_runs:
        edx_grade_user_iter = exception_logging_generator(
            get_edx_grades_with_users(run)
        )
        created_grades_count, updated_grades_count, generated_certificates_count = (
            0,
            0,
            0,
        )
        for edx_grade, user in edx_grade_user_iter:
            course_run_grade, created, updated = ensure_course_run_grade(
                user=user, course_run=run, edx_grade=edx_grade, should_update=True
            )

            if created:
                created_grades_count += 1
            elif updated:
                updated_grades_count += 1

            # Check certificate generation eligibility
            #   1. For self_paced course runs we generate certificates right away irrespective of end_date
            #   2. For others course runs we generate the certificates if the end of course run has passed
            if run.is_self_paced or (run.end_date and run.end_date <= now):
                _, created, deleted = process_course_run_grade_certificate(
                    course_run_grade=course_run_grade
                )

                if deleted:
                    log.warning(
                        "Certificate deleted for user %s and course_run %s", user, run
                    )
                elif created:
                    log.warning(
                        "Certificate created for user %s and course_run %s", user, run
                    )
                    generated_certificates_count += 1
        log.info(
            f"Finished processing course run {run}: created grades for {created_grades_count} users, updated grades for {updated_grades_count} users, generated certificates for {generated_certificates_count} users"
        )


def manage_course_run_certificate_access(user, courseware_id, revoke_state):
    """
    Revokes/Un-Revokes a course run certificate.

    Args:
        user (User): a Django user.
        courseware_id (str): A string representing the course run's courseware_id.
        revoke_state (bool): A flag representing True(Revoke), False(Un-Revoke)

    Returns:
        bool: A boolean representing the revoke/unrevoke success
    """
    course_run = CourseRun.objects.get(courseware_id=courseware_id)

    try:
        course_run_certificate = CourseRunCertificate.all_objects.get(
            user=user, course_run=course_run
        )
    except CourseRunCertificate.DoesNotExist:
        log.warning(
            "Course run certificate for user: %s and course_run: %s does not exist.",
            user.username,
            course_run,
        )
        return False

    course_run_certificate.is_revoked = revoke_state
    course_run_certificate.save()

    return True


def override_user_grade(user, override_grade, courseware_id, should_force_pass=False):
    """Override grade for a user

    Args:
        user (User): a Django user.
        courseware_id (str): A string representing the course run's courseware_id.
        override_grade (float): A float value for the grade override between (0.0 and 1.0) - 0.0 would mean passed=False
        should_force_pass (bool): A flag representing if user should mark as passed forcefully (In this case we don't know
        the grading policy based in edX so we manually take a value for forcing the passed status)
    Returns:
        (CourseRunGrade): The updates grade of the user
    """

    if not is_grade_valid(override_grade):
        raise ValidationError("Invalid value for grade. Allowed range: 0.0 - 1.0")

    with transaction.atomic():
        course_run_grade = CourseRunGrade.objects.select_for_update().get(
            user=user, course_run__courseware_id=courseware_id
        )
        course_run_grade.grade = override_grade
        course_run_grade.passed = bool(override_grade) if should_force_pass else False
        course_run_grade.letter_grade = None
        course_run_grade.set_by_admin = True
        course_run_grade.save_and_log(None)

    return course_run_grade
