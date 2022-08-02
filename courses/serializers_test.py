"""
Tests for course serializers
"""
# pylint: disable=unused-argument, redefined-outer-name
from datetime import datetime, timedelta

import factory
import pytest
import pytz
from django.contrib.auth.models import AnonymousUser

from cms.factories import CoursePageFactory, FlexiblePricingFormFactory
from courses.factories import (
    CourseFactory,
    CourseRunEnrollmentFactory,
    CourseRunFactory,
    ProgramEnrollmentFactory,
    ProgramFactory,
)
from courses.models import CourseTopic
from courses.serializers import (
    BaseCourseSerializer,
    BaseProgramSerializer,
    CourseRunDetailSerializer,
    CourseRunEnrollmentSerializer,
    CourseRunSerializer,
    CourseSerializer,
    ProgramEnrollmentSerializer,
    ProgramSerializer,
)
from ecommerce.serializers import BaseProductSerializer
from main.test_utils import assert_drf_json_equal, drf_datetime

pytestmark = [pytest.mark.django_db]


def test_base_program_serializer():
    """Test BaseProgramSerializer serialization"""
    program = ProgramFactory.create()
    data = BaseProgramSerializer(program).data
    assert data == {
        "title": program.title,
        "readable_id": program.readable_id,
        "id": program.id,
    }


def test_serialize_program(mock_context):
    """Test Program serialization"""
    program = ProgramFactory.create()
    run1 = CourseRunFactory.create(course__program=program)
    course1 = run1.course
    run2 = CourseRunFactory.create(course__program=program)
    course2 = run2.course
    runs = (
        [run1, run2]
        + [CourseRunFactory.create(course=course1) for _ in range(2)]
        + [CourseRunFactory.create(course=course2) for _ in range(2)]
    )
    topics = [CourseTopic.objects.create(name=f"topic{num}") for num in range(3)]
    course1.topics.set([topics[0], topics[1]])
    course2.topics.set([topics[1], topics[2]])

    data = ProgramSerializer(instance=program, context=mock_context).data

    assert_drf_json_equal(
        data,
        {
            "title": program.title,
            "readable_id": program.readable_id,
            "id": program.id,
            "courses": [
                CourseSerializer(instance=course, context={**mock_context}).data
                for course in [course1, course2]
            ],
            "start_date": drf_datetime(
                sorted(runs, key=lambda run: run.start_date)[0].start_date
            ),
            "end_date": drf_datetime(
                sorted(runs, key=lambda run: run.end_date)[-1].end_date
            ),
            "enrollment_start": drf_datetime(
                sorted(runs, key=lambda run: run.enrollment_start)[0].enrollment_start
            ),
            "topics": [{"name": topic.name} for topic in topics],
        },
    )


def test_base_course_serializer():
    """Test CourseRun serialization"""
    course = CourseFactory.create()
    data = BaseCourseSerializer(course).data
    assert data == {
        "title": course.title,
        "readable_id": course.readable_id,
        "id": course.id,
    }


@pytest.mark.parametrize("is_anonymous", [True, False])
@pytest.mark.parametrize("all_runs", [True, False])
def test_serialize_course(mock_context, is_anonymous, all_runs):
    """Test Course serialization"""
    now = datetime.now(tz=pytz.UTC)
    if is_anonymous:
        mock_context["request"].user = AnonymousUser()
    if all_runs:
        mock_context["all_runs"] = True
    user = mock_context["request"].user
    course_run = CourseRunFactory.create(course__no_program=True, live=True)
    course = course_run.course
    topic = "a course topic"
    course.topics.set([CourseTopic.objects.create(name=topic)])

    # Create expired, enrollment_ended, future, and enrolled course runs
    CourseRunFactory.create(course=course, end_date=now - timedelta(1), live=True)
    CourseRunFactory.create(course=course, enrollment_end=now - timedelta(1), live=True)
    CourseRunFactory.create(
        course=course, enrollment_start=now + timedelta(1), live=True
    )
    enrolled_run = CourseRunFactory.create(course=course, live=True)
    unexpired_runs = [enrolled_run, course_run]
    CourseRunEnrollmentFactory.create(
        run=enrolled_run, **({} if is_anonymous else {"user": user})
    )

    data = CourseSerializer(instance=course, context=mock_context).data

    if all_runs or is_anonymous:
        expected_runs = unexpired_runs
    else:
        expected_runs = [course_run]

    assert_drf_json_equal(
        data,
        {
            "title": course.title,
            "readable_id": course.readable_id,
            "id": course.id,
            "courseruns": [
                CourseRunSerializer(run).data
                for run in sorted(expected_runs, key=lambda run: run.start_date)
            ],
            "next_run_id": course.first_unexpired_run.id,
            "topics": [{"name": topic}],
        },
    )


@pytest.mark.parametrize("financial_assistance_available", [True, False])
def test_serialize_course_with_page_fields(
    mocker, mock_context, financial_assistance_available
):
    """
    Tests course serialization with Page fields and Financial Assistance form.
    """
    fake_image_src = "http://example.com/my.img"
    patched_get_wagtail_src = mocker.patch(
        "cms.serializers.get_wagtail_img_src", return_value=fake_image_src
    )
    if financial_assistance_available:
        financial_assistance_form = FlexiblePricingFormFactory()
        course_page = financial_assistance_form.get_parent()
        expected_financial_assistance_url = (
            f"{course_page.get_url()}{financial_assistance_form.slug}/"
        )
    else:
        course_page = CoursePageFactory.create()
        expected_financial_assistance_url = ""
    course = course_page.course
    data = BaseCourseSerializer(
        instance=course, context={**mock_context, "include_page_fields": True}
    ).data
    assert_drf_json_equal(
        data,
        {
            "title": course.title,
            "readable_id": course.readable_id,
            "id": course.id,
            "feature_image_src": fake_image_src,
            "page_url": None,
            "financial_assistance_form_url": expected_financial_assistance_url,
        },
    )
    patched_get_wagtail_src.assert_called_once_with(course_page.feature_image)


def test_serialize_course_run():
    """Test CourseRun serialization"""
    course_run = CourseRunFactory.create()
    course_run.refresh_from_db()

    data = CourseRunSerializer(course_run).data
    assert_drf_json_equal(
        data,
        {
            "title": course_run.title,
            "courseware_id": course_run.courseware_id,
            "run_tag": course_run.run_tag,
            "courseware_url": course_run.courseware_url,
            "start_date": drf_datetime(course_run.start_date),
            "end_date": drf_datetime(course_run.end_date),
            "enrollment_start": drf_datetime(course_run.enrollment_start),
            "enrollment_end": drf_datetime(course_run.enrollment_end),
            "expiration_date": drf_datetime(course_run.expiration_date),
            "id": course_run.id,
            "products": [],
            "page": None,
        },
    )


def test_serialize_course_run_detail():
    """Test CourseRunDetailSerializer serialization"""
    course_run = CourseRunFactory.create()
    data = CourseRunDetailSerializer(course_run).data

    assert data == {
        "course": BaseCourseSerializer(course_run.course).data,
        "course_number": course_run.course_number,
        "title": course_run.title,
        "courseware_id": course_run.courseware_id,
        "courseware_url": course_run.courseware_url,
        "start_date": drf_datetime(course_run.start_date),
        "end_date": drf_datetime(course_run.end_date),
        "enrollment_start": drf_datetime(course_run.enrollment_start),
        "enrollment_end": drf_datetime(course_run.enrollment_end),
        "expiration_date": drf_datetime(course_run.expiration_date),
        "id": course_run.id,
        "products": BaseProductSerializer(course_run.products, many=True).data,
        "page": None,
    }


@pytest.mark.parametrize("receipts_enabled", [True, False])
def test_serialize_course_run_enrollments(settings, receipts_enabled):
    """Test that CourseRunEnrollmentSerializer has correct data"""
    settings.ENABLE_ORDER_RECEIPTS = receipts_enabled
    course_run_enrollment = CourseRunEnrollmentFactory.create()
    serialized_data = CourseRunEnrollmentSerializer(course_run_enrollment).data
    assert serialized_data == {
        "run": CourseRunDetailSerializer(course_run_enrollment.run).data,
        "id": course_run_enrollment.id,
        "edx_emails_subscription": True,
        "enrollment_mode": "audit",
    }


def test_serialize_program_enrollments_assert():
    """Test that ProgramEnrollmentSerializer throws an error when course run enrollments aren't provided"""
    program_enrollment = ProgramEnrollmentFactory.build()
    with pytest.raises(AssertionError):
        ProgramEnrollmentSerializer(program_enrollment)


@pytest.mark.parametrize("receipts_enabled", [True, False])
def test_serialize_program_enrollments(settings, receipts_enabled):
    """Test that ProgramEnrollmentSerializer has correct data"""
    settings.ENABLE_ORDER_RECEIPTS = receipts_enabled
    program = ProgramFactory.create()
    course_run_enrollments = CourseRunEnrollmentFactory.create_batch(
        3,
        run__course__program=factory.Iterator([program, program, None]),
        run__course__position_in_program=factory.Iterator([2, 1, None]),
    )
    program_enrollment = ProgramEnrollmentFactory.create(
        program=program,
    )
    serialized_data = ProgramEnrollmentSerializer(
        program_enrollment, context={"course_run_enrollments": course_run_enrollments}
    ).data
    assert serialized_data == {
        "id": program_enrollment.id,
        "program": BaseProgramSerializer(program).data,
        # Only enrollments for the given program should be serialized, and they should be
        # sorted by position in program.
        "course_run_enrollments": CourseRunEnrollmentSerializer(
            [course_run_enrollments[1], course_run_enrollments[0]], many=True
        ).data,
    }
