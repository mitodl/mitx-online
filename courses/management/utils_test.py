"""Tests for command utils"""
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from mitol.common.utils.datetime import now_in_utc

from courses.factories import (
    CourseRunEnrollmentFactory,
    CourseRunFactory,
    ProgramEnrollmentFactory,
)
from courses.management.utils import EnrollmentChangeCommand
from main.test_utils import MockHttpError
from openedx.constants import EDX_DEFAULT_ENROLLMENT_MODE
from openedx.exceptions import EdxApiEnrollErrorException, UnknownEdxApiEnrollException
from users.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_fetch_enrollment():
    """Test that method return enrollment and enrolled object"""
    user = UserFactory()
    run_enrollment = CourseRunEnrollmentFactory(user=user)
    program_enrollment = ProgramEnrollmentFactory(user=user)

    run_command_options = {"run": run_enrollment.run.courseware_id}
    program_command_options = {"program": program_enrollment.program.readable_id}

    enrollment_obj, enrolled_obj = EnrollmentChangeCommand.fetch_enrollment(
        user=user, command_options=run_command_options
    )

    assert enrolled_obj == run_enrollment.run
    assert enrollment_obj == run_enrollment

    enrollment_obj, enrolled_obj = EnrollmentChangeCommand.fetch_enrollment(
        user=user, command_options=program_command_options
    )

    assert enrolled_obj == program_enrollment.program
    assert enrollment_obj == program_enrollment


@pytest.mark.django_db
@pytest.mark.parametrize("keep_failed_enrollments", [True, False])
@pytest.mark.parametrize(
    "exception_cls,inner_exception",
    [
        [EdxApiEnrollErrorException, MockHttpError()],
        [UnknownEdxApiEnrollException, Exception()],
    ],
)
def test_create_run_enrollment_edx_failure(
    mocker, keep_failed_enrollments, exception_cls, inner_exception
):
    """Test that create_run_enrollment behaves as expected when the enrollment fails in edX"""
    now = now_in_utc()
    user = UserFactory()
    existing_enrollment = CourseRunEnrollmentFactory(user=user)
    non_program_run = CourseRunFactory.create(
        course__no_program=True, start_date=(now + timedelta(days=1))
    )
    expected_enrollment = CourseRunEnrollmentFactory(user=user, run=non_program_run)

    patched_edx_enroll = mocker.patch(
        "courses.management.utils.enroll_in_edx_course_runs",
        side_effect=exception_cls(user, non_program_run, inner_exception),
    )

    new_enrollment = EnrollmentChangeCommand().create_run_enrollment(
        existing_enrollment=existing_enrollment,
        to_user=user,
        to_run=non_program_run,
        keep_failed_enrollments=keep_failed_enrollments,
    )

    patched_edx_enroll.assert_called_once_with(user, [non_program_run])

    if keep_failed_enrollments:
        assert new_enrollment == expected_enrollment
    else:
        assert new_enrollment is None
