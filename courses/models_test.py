"""Tests for course models"""
from datetime import timedelta
from types import SimpleNamespace

import factory
import pytest
from django.core.exceptions import ValidationError
from mitol.common.utils.datetime import now_in_utc

from courses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from courses.factories import (
    CourseFactory,
    CourseRunEnrollmentFactory,
    CourseRunFactory,
    CourseRunCertificateFactory,
    ProgramEnrollmentFactory,
    ProgramFactory,
)
from courses.models import Course, CourseRunEnrollment, ProgramRequirement
from main.test_utils import format_as_iso8601
from users.factories import UserFactory

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def program_with_requirements():
    program = ProgramFactory.create()
    required_courses = CourseFactory.create_batch(3, program=program)
    elective_courses = CourseFactory.create_batch(3, program=program)
    mut_exclusive_courses = CourseFactory.create_batch(3, program=program)

    root_node = ProgramRequirement.add_root(program=program)

    required_courses_node = root_node.add_child(
        operator=ProgramRequirement.Operator.ALL_OF, title="Required Courses"
    )
    for course in required_courses:
        required_courses_node.add_child(course=course)

    # at least two must be taken
    elective_courses_node = root_node.add_child(
        operator=ProgramRequirement.Operator.MIN_NUMBER_OF,
        operator_value=2,
        title="Elective Courses",
    )
    for course in elective_courses:
        elective_courses_node.add_child(course=course)

    # 3rd elective option is at least one of these courses
    mut_exclusive_courses_node = elective_courses_node.add_child(
        operator=ProgramRequirement.Operator.MIN_NUMBER_OF, operator_value=1
    )
    for course in mut_exclusive_courses:
        mut_exclusive_courses_node.add_child(course=course)

    return SimpleNamespace(
        program=program,
        root_node=root_node,
        required_courses=required_courses,
        required_courses_node=required_courses_node,
        elective_courses=elective_courses,
        elective_courses_node=elective_courses_node,
        mut_exclusive_courses=mut_exclusive_courses,
        mut_exclusive_courses_node=mut_exclusive_courses_node,
    )


def test_program_course_auto_position():
    """
    If a course is added to a program with no position specified, it should be given the last position
    """
    first_course = CourseFactory.create(position_in_program=None)
    assert first_course.position_in_program == 1
    second_course = CourseFactory.create(
        program=first_course.program, position_in_program=None
    )
    assert second_course.position_in_program == 2


def test_program_num_courses():
    """
    Program should return number of courses associated with it
    """
    program = ProgramFactory.create()
    assert program.num_courses == 0

    CourseFactory.create(program=program)
    assert program.num_courses == 1

    CourseFactory.create(program=program)
    assert program.num_courses == 2


def test_program_next_run_date():
    """
    next_run_date should return the date of the CourseRun with the nearest future start date
    and first position in program (course__position_in_program=1)
    """
    program = ProgramFactory.create()
    CourseRunFactory.create_batch(
        2,
        course=CourseFactory.create(program=program, position_in_program=3),
        past_start=True,
    )
    assert program.next_run_date is None

    now = now_in_utc()
    second_course_future_dates = [now + timedelta(hours=1), now + timedelta(hours=3)]
    CourseRunFactory.create_batch(
        2,
        course=CourseFactory.create(program=program, position_in_program=2),
        start_date=factory.Iterator(second_course_future_dates),
        live=True,
    )

    first_course_future_dates = [now + timedelta(hours=2), now + timedelta(hours=4)]
    CourseRunFactory.create_batch(
        2,
        course=CourseFactory.create(program=program, position_in_program=1),
        start_date=factory.Iterator(first_course_future_dates),
        live=True,
    )

    # invalidate cached property
    del program.next_run_date

    assert program.next_run_date == first_course_future_dates[0]


def test_program_is_catalog_visible():
    """
    is_catalog_visible should return True if a program has any course run that has a start date or enrollment end
    date in the future
    """
    program = ProgramFactory.create()
    runs = CourseRunFactory.create_batch(
        2, course__program=program, past_start=True, past_enrollment_end=True
    )
    assert program.is_catalog_visible is False

    now = now_in_utc()
    run = runs[0]
    run.start_date = now + timedelta(hours=1)
    run.save()
    assert program.is_catalog_visible is True

    run.start_date = now - timedelta(hours=1)
    run.enrollment_end = now + timedelta(hours=1)
    run.save()
    assert program.is_catalog_visible is True


def test_program_first_course_unexpired_runs():
    """
    first_course_unexpired_runs should return the unexpired course runs of the first course
    in the program (position_in_program=1)
    """
    program = ProgramFactory.create()

    now = now_in_utc()
    past_start_dates = [
        now + timedelta(days=-10),
        now + timedelta(days=-11),
        now + timedelta(days=-12),
    ]

    past_end_dates = [now + timedelta(days=-5), now + timedelta(days=-6)]
    future_end_dates = [
        now + timedelta(days=10),
        now + timedelta(days=11),
        now + timedelta(days=12),
    ]

    first_course = CourseFactory.create(
        live=True, program=program, position_in_program=1
    )
    second_course = CourseFactory.create(
        live=True, program=program, position_in_program=2
    )

    CourseRunFactory.create_batch(
        2,
        course=second_course,
        start_date=factory.Iterator(past_start_dates),
        end_date=factory.Iterator(past_end_dates),
        live=True,
    )
    CourseRunFactory.create_batch(
        3,
        course=first_course,
        start_date=factory.Iterator(past_start_dates),
        end_date=factory.Iterator(future_end_dates),
        enrollment_end=factory.Iterator(future_end_dates),
        live=True,
    )
    assert len(program.first_course_unexpired_runs) == 3


def test_courseware_url(settings):
    """Test that the courseware_url property yields the correct values"""
    settings.OPENEDX_BASE_REDIRECT_URL = "http://example.com"
    course_run = CourseRunFactory.build(courseware_url_path="/path")
    course_run_no_path = CourseRunFactory.build(courseware_url_path=None)
    assert course_run.courseware_url == "http://example.com/path"
    assert course_run_no_path.courseware_url is None


@pytest.mark.parametrize("end_days,expected", [[-1, True], [1, False], [None, False]])
def test_course_run_past(end_days, expected):
    """
    Test that CourseRun.is_past returns the expected boolean value
    """
    now = now_in_utc()
    end_date = None if end_days is None else (now + timedelta(days=end_days))
    assert CourseRunFactory.create(end_date=end_date).is_past is expected


@pytest.mark.parametrize(
    "upgrade_deadline_days,expected", [[-1, False], [1, True], [None, True]]
)
def test_course_run_upgradeable(upgrade_deadline_days, expected):
    """
    Test that CourseRun.is_upgradable returns the expected boolean value
    """
    now = now_in_utc()
    upgrade_deadline = (
        None
        if upgrade_deadline_days is None
        else (now + timedelta(days=upgrade_deadline_days))
    )
    assert (
        CourseRunFactory.create(upgrade_deadline=upgrade_deadline).is_upgradable
        is expected
    )


@pytest.mark.parametrize(
    "start_delta, end_delta, expiration_delta", [[-1, 2, 3], [1, 3, 4], [10, 20, 30]]
)
def test_course_run_expiration_date(start_delta, end_delta, expiration_delta):
    """
    Test that CourseRun.expiration_date returns the expected value
    """
    now = now_in_utc()
    expiration_date = now + timedelta(days=expiration_delta)
    assert (
        CourseRunFactory.create(
            start_date=now + timedelta(days=start_delta),
            end_date=now + timedelta(days=end_delta),
            expiration_date=expiration_date,
        ).expiration_date
        == expiration_date
    )


@pytest.mark.parametrize(
    "start_delta, end_delta, expiration_delta", [[1, 2, 1], [1, 2, -1]]
)
def test_course_run_invalid_expiration_date(start_delta, end_delta, expiration_delta):
    """
    Test that CourseRun.expiration_date raises ValidationError if expiration_date is before start_date or end_date
    """
    now = now_in_utc()
    with pytest.raises(ValidationError):
        CourseRunFactory.create(
            start_date=now + timedelta(days=start_delta),
            end_date=now + timedelta(days=end_delta),
            expiration_date=now + timedelta(days=expiration_delta),
        )


@pytest.mark.parametrize(
    "end_days, enroll_start_days, enroll_end_days, expected",
    [
        [None, None, None, True],
        [None, None, 1, True],
        [None, None, -1, False],
        [1, None, None, True],
        [-1, None, None, False],
        [1, None, -1, False],
        [None, 1, None, False],
        [None, -1, None, True],
    ],
)
def test_course_run_not_beyond_enrollment(
    end_days, enroll_start_days, enroll_end_days, expected
):
    """
    Test that CourseRun.is_beyond_enrollment returns the expected boolean value
    """
    now = now_in_utc()
    end_date = None if end_days is None else now + timedelta(days=end_days)
    enr_end_date = (
        None if enroll_end_days is None else now + timedelta(days=enroll_end_days)
    )
    enr_start_date = (
        None if enroll_start_days is None else now + timedelta(days=enroll_start_days)
    )

    assert (
        CourseRunFactory.create(
            end_date=end_date,
            enrollment_end=enr_end_date,
            enrollment_start=enr_start_date,
        ).is_not_beyond_enrollment
        is expected
    )


@pytest.mark.parametrize(
    "start_delta, end_delta, expected_result",
    [
        [-1, 2, True],
        [-1, None, True],
        [None, 2, False],
        [-2, -1, False],
    ],
)
def test_course_run_in_progress(start_delta, end_delta, expected_result):
    """
    Test that CourseRun.is_in_progress returns the correct value based on the start and end dates
    """
    now = now_in_utc()
    start_date = None if start_delta is None else now + timedelta(days=start_delta)
    end_date = None if end_delta is None else now + timedelta(days=end_delta)
    assert (
        CourseRunFactory.create(
            start_date=start_date,
            end_date=end_date,
            expiration_date=now + timedelta(days=10),
        ).is_in_progress
        is expected_result
    )


@pytest.mark.parametrize(
    "end_days,enroll_days,expected", [[-1, 1, False], [1, -1, False], [1, 1, True]]
)
def test_course_run_unexpired(end_days, enroll_days, expected):
    """
    Test that CourseRun.is_unexpired returns the expected boolean value
    """
    now = now_in_utc()
    end_date = now + timedelta(days=end_days)
    enr_end_date = now + timedelta(days=enroll_days)
    assert (
        CourseRunFactory.create(
            end_date=end_date, enrollment_end=enr_end_date
        ).is_unexpired
        is expected
    )


def test_course_first_unexpired_run():
    """
    Test that the first unexpired run of a course is returned
    """
    course = CourseFactory.create()
    now = now_in_utc()
    end_date = now + timedelta(days=100)
    enr_end_date = now + timedelta(days=100)
    first_run = CourseRunFactory.create(
        start_date=now,
        course=course,
        end_date=end_date,
        enrollment_end=enr_end_date,
        live=True,
    )
    CourseRunFactory.create(
        start_date=now + timedelta(days=50),
        course=course,
        end_date=end_date,
        enrollment_end=enr_end_date,
    )
    assert course.first_unexpired_run == first_run


def test_program_first_unexpired_run():
    """
    Test that the first unexpired run of a program is returned
    """
    program = ProgramFactory()
    course = CourseFactory.create(program=program)
    now = now_in_utc()
    end_date = now + timedelta(days=100)
    enr_end_date = now + timedelta(days=100)
    first_run = CourseRunFactory.create(
        start_date=now,
        course=course,
        end_date=end_date,
        enrollment_end=enr_end_date,
        live=True,
    )

    # create another course and course run in program
    another_course = CourseFactory.create(program=program)
    second_run = CourseRunFactory.create(
        start_date=now + timedelta(days=50),
        course=another_course,
        end_date=end_date,
        enrollment_end=enr_end_date,
    )

    assert first_run.start_date < second_run.start_date
    assert program.first_unexpired_run == first_run


def test_course_next_run_date():
    """
    next_run_date should return the date of the CourseRun with the nearest future start date
    """
    course = CourseFactory.create()
    CourseRunFactory.create_batch(2, course=course, past_start=True, live=True)
    assert course.next_run_date is None

    now = now_in_utc()
    future_dates = [now + timedelta(hours=1), now + timedelta(hours=2)]
    CourseRunFactory.create_batch(
        2, course=course, start_date=factory.Iterator(future_dates), live=True
    )

    # invlidate cached property
    del course.next_run_date

    assert course.next_run_date == future_dates[0]


def test_course_is_catalog_visible():
    """
    is_catalog_visible should return True if a course has any course run that has a start date or enrollment end
    date in the future
    """
    course = CourseFactory.create()
    runs = CourseRunFactory.create_batch(
        2, course=course, past_start=True, past_enrollment_end=True
    )
    assert course.is_catalog_visible is False

    now = now_in_utc()
    run = runs[0]
    run.start_date = now + timedelta(hours=1)
    run.save()
    assert course.is_catalog_visible is True

    run.start_date = now - timedelta(hours=1)
    run.enrollment_end = now + timedelta(hours=1)
    run.save()
    assert course.is_catalog_visible is True


def test_course_unexpired_runs():
    """unexpired_runs should return expected value"""
    course = CourseFactory.create()
    now = now_in_utc()
    start_dates = [now, now + timedelta(days=-3)]
    end_dates = [now + timedelta(hours=1), now + timedelta(days=-2)]
    CourseRunFactory.create_batch(
        2,
        course=course,
        start_date=factory.Iterator(start_dates),
        end_date=factory.Iterator(end_dates),
        live=True,
    )

    # Add a run that is not live and shouldn't show up in unexpired list
    CourseRunFactory.create(
        course=course, start_date=start_dates[0], end_date=end_dates[0], live=False
    )

    assert len(course.unexpired_runs) == 1
    course_run = course.unexpired_runs[0]
    assert course_run.start_date == start_dates[0]
    assert course_run.end_date == end_dates[0]


def test_course_available_runs():
    """enrolled runs for a user should not be in the list of available runs"""
    user = UserFactory.create()
    course = CourseFactory.create()
    runs = CourseRunFactory.create_batch(2, course=course, live=True)
    runs.sort(key=lambda run: run.start_date)
    CourseRunEnrollmentFactory.create(run=runs[0], user=user)
    assert course.available_runs(user) == [runs[1]]
    assert course.available_runs(UserFactory.create()) == runs


def test_reactivate_and_save():
    """Test that the reactivate_and_save method in enrollment models sets properties and saves"""
    course_run_enrollment = CourseRunEnrollmentFactory.create(
        active=False, change_status=ENROLL_CHANGE_STATUS_REFUNDED
    )
    program_enrollment = ProgramEnrollmentFactory.create(
        active=False, change_status=ENROLL_CHANGE_STATUS_REFUNDED
    )
    enrollments = [course_run_enrollment, program_enrollment]
    for enrollment in enrollments:
        enrollment.reactivate_and_save()
        enrollment.refresh_from_db()
        enrollment.active = True
        enrollment.change_status = None


def test_deactivate_and_save():
    """Test that the deactivate_and_save method in enrollment models sets properties and saves"""
    course_run_enrollment = CourseRunEnrollmentFactory.create(
        active=True, change_status=None
    )
    program_enrollment = ProgramEnrollmentFactory.create(
        active=True, change_status=None
    )
    enrollments = [course_run_enrollment, program_enrollment]
    for enrollment in enrollments:
        enrollment.deactivate_and_save(ENROLL_CHANGE_STATUS_REFUNDED)
        enrollment.refresh_from_db()
        enrollment.active = False
        enrollment.change_status = ENROLL_CHANGE_STATUS_REFUNDED


@pytest.mark.parametrize(
    "readable_id_value",
    ["somevalue", "some-value", "some_value", "some+value", "some:value"],
)
def test_readable_id_valid(readable_id_value):
    """
    Test that the Program/Course readable_id field accepts valid values, and that
    validation is performed when a save is attempted.
    """
    program = ProgramFactory.build(readable_id=readable_id_value)
    program.save()
    assert program.id is not None
    course = CourseFactory.build(program=None, readable_id=readable_id_value)
    course.save()
    assert course.id is not None


@pytest.mark.parametrize(
    "readable_id_value",
    [
        "",
        "some value",
        "some/value",
        " somevalue",
        "somevalue ",
        "/somevalue",
        "somevalue/",
    ],
)
def test_readable_id_invalid(readable_id_value):
    """
    Test that the Program/Course readable_id field rejects invalid values, and that
    validation is performed when a save is attempted.
    """
    program = ProgramFactory.build(readable_id=readable_id_value)
    with pytest.raises(ValidationError):
        program.save()
    course = CourseFactory.build(program=None, readable_id=readable_id_value)
    with pytest.raises(ValidationError):
        course.save()


def test_get_program_run_enrollments(user):
    """
    Test that the get_program_run_enrollments helper method for CourseRunEnrollment returns
    the appropriate course run enrollments for a program
    """
    programs = ProgramFactory.create_batch(2)
    program = programs[0]
    course_run_enrollments = CourseRunEnrollmentFactory.create_batch(
        2,
        user=user,
        run__course__program=factory.Iterator([program, program, programs[1]]),
    )
    expected_run_enrollments = set(course_run_enrollments[0:2])
    assert (
        set(CourseRunEnrollment.get_program_run_enrollments(user, program))
        == expected_run_enrollments
    )


@pytest.mark.parametrize("is_program", [True, False])
def test_audit(user, is_program):
    """Test audit table serialization"""
    enrollment = (
        ProgramEnrollmentFactory.create()
        if is_program
        else CourseRunEnrollmentFactory.create()
    )

    enrollment.save_and_log(user)

    expected = {
        "active": enrollment.active,
        "change_status": enrollment.change_status,
        "created_on": format_as_iso8601(enrollment.created_on),
        "email": enrollment.user.email,
        "full_name": enrollment.user.name,
        "id": enrollment.id,
        "text_id": enrollment.program.readable_id
        if is_program
        else enrollment.run.courseware_id,
        "updated_on": format_as_iso8601(enrollment.updated_on),
        "user": enrollment.user.id,
        "username": enrollment.user.username,
        "enrollment_mode": enrollment.enrollment_mode,
    }
    if not is_program:
        expected["edx_enrolled"] = enrollment.edx_enrolled
        expected["run"] = enrollment.run.id
        expected["edx_emails_subscription"] = True
    else:
        expected["program"] = enrollment.program.id
    assert (
        enrollment.get_audit_class().objects.get(enrollment=enrollment).data_after
        == expected
    )


def test_enrollment_is_ended():
    """Verify that is_ended returns True, if all of course runs in a program/course are ended."""
    past_date = now_in_utc() - timedelta(days=1)
    past_program = ProgramFactory.create()
    past_course = CourseFactory.create()

    past_course_runs = CourseRunFactory.create_batch(
        3, end_date=past_date, course=past_course, course__program=past_program
    )

    program_enrollment = ProgramEnrollmentFactory.create(program=past_program)
    course_enrollment = CourseRunEnrollmentFactory.create(run=past_course_runs[0])

    assert program_enrollment.is_ended
    assert course_enrollment.is_ended


def test_course_run_certificate_start_end_dates():
    """
    Test that the CourseRunCertificate start_end_dates property works properly
    """
    certificate = CourseRunCertificateFactory.create()
    start_date, end_date = certificate.start_end_dates
    assert start_date == certificate.course_run.start_date
    assert end_date == certificate.course_run.end_date


def test_course_course_number():
    """
    Test that the Course course_number property works correctly with the readable_id.
    """
    course = CourseFactory.build(readable_id="course-v1:TestX+Test101")
    assert "Test101" == course.course_number


def test_program_requirements(program_with_requirements):
    """Test for program requirements"""
    node_defaults = {
        "course": None,
        "operator": None,
        "operator_value": None,
        "title": "",
        "program": program_with_requirements.program.id,
    }

    assert program_with_requirements.root_node.dump_bulk() == [
        {
            "data": {
                **node_defaults,
            },
            "id": program_with_requirements.root_node.id,
            "children": [
                {
                    "data": {
                        **node_defaults,
                        "operator": ProgramRequirement.Operator.ALL_OF.value,
                        "title": "Required Courses",
                    },
                    "id": program_with_requirements.required_courses_node.id,
                    "children": [
                        {
                            "data": {
                                **node_defaults,
                                "course": course.id,
                            },
                            "id": node.id,
                        }
                        for course, node in zip(
                            program_with_requirements.required_courses,
                            program_with_requirements.required_courses_node.get_children(),
                        )
                    ],
                },
                {
                    "data": {
                        **node_defaults,
                        "operator": ProgramRequirement.Operator.MIN_NUMBER_OF.value,
                        "operator_value": "2",
                        "title": "Elective Courses",
                    },
                    "id": program_with_requirements.elective_courses_node.id,
                    "children": [
                        *[
                            {
                                "data": {
                                    **node_defaults,
                                    "course": course.id,
                                },
                                "id": node.id,
                            }
                            for course, node in zip(
                                program_with_requirements.elective_courses,
                                program_with_requirements.elective_courses_node.get_children(),
                            )
                        ],
                        {
                            "data": {
                                **node_defaults,
                                "operator": ProgramRequirement.Operator.MIN_NUMBER_OF.value,
                                "operator_value": "1",
                            },
                            "id": program_with_requirements.mut_exclusive_courses_node.id,
                            "children": [
                                {
                                    "data": {
                                        **node_defaults,
                                        "course": course.id,
                                    },
                                    "id": node.id,
                                }
                                for course, node in zip(
                                    program_with_requirements.mut_exclusive_courses,
                                    program_with_requirements.mut_exclusive_courses_node.get_children(),
                                )
                            ],
                        },
                    ],
                },
            ],
        }
    ]


@pytest.mark.parametrize("operator", ProgramRequirement.Operator.values)
def test_program_requirements_is_operator(operator):
    """Test that is_operator is True for known operators"""
    assert ProgramRequirement(operator=operator).is_operator is True


@pytest.mark.parametrize(
    "operator, expected",
    [
        (ProgramRequirement.Operator.ALL_OF.value, True),
        (ProgramRequirement.Operator.MIN_NUMBER_OF.value, False),
    ],
)
def test_program_requirements_is_all_of_operator(operator, expected):
    """Test is_all_of_operator"""
    assert ProgramRequirement(operator=operator).is_all_of_operator is expected


@pytest.mark.parametrize(
    "operator, expected",
    [
        (ProgramRequirement.Operator.ALL_OF.value, False),
        (ProgramRequirement.Operator.MIN_NUMBER_OF.value, True),
    ],
)
def test_program_requirements_is_min_number_of_operator(operator, expected):
    """Test is_min_number_of_operator"""
    assert ProgramRequirement(operator=operator).is_min_number_of_operator is expected


def test_courses_in_program(program_with_requirements):
    """Test CourseQuerySet.courses_in_program"""
    CourseFactory.create_batch(4)

    courses = Course.objects.courses_in_program(program_with_requirements.program)

    assert set(courses) == set(
        program_with_requirements.required_courses
        + program_with_requirements.elective_courses
        + program_with_requirements.mut_exclusive_courses
    )
