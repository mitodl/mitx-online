"""
Tests for cms serializers
"""
import bleach
import pytest
from django.test.client import RequestFactory

from cms.factories import (
    CoursePageFactory,
    FlexiblePricingFormFactory,
    ProgramPageFactory,
)
from cms.models import FlexiblePricingRequestForm
from cms.serializers import CoursePageSerializer
from courses.factories import (
    CourseFactory,
    ProgramFactory,
    program_with_empty_requirements,
    program_with_requirements,
)
from main.test_utils import assert_drf_json_equal

pytestmark = [pytest.mark.django_db]


def test_serialize_course_page(
    mocker, fully_configured_wagtail, staff_user, mock_context
):
    """
    Tests course page serialization with Financial Assistance form with a parent-child relationship
    with a course, but no program.
    """
    fake_image_src = "http://example.com/my.img"
    patched_get_wagtail_src = mocker.patch(
        "cms.serializers.get_wagtail_img_src", return_value=fake_image_src
    )

    rf = RequestFactory()
    request = rf.get("/")
    request.user = staff_user

    course_page = CoursePageFactory()
    course_page.product.program = None
    FlexiblePricingFormFactory(parent=course_page)

    financial_assistance_page = (
        course_page.get_children().type(FlexiblePricingRequestForm).live().first()
    )

    data = CoursePageSerializer(
        instance=course_page, context=course_page.get_context(request)
    ).data
    assert_drf_json_equal(
        data,
        {
            "feature_image_src": fake_image_src,
            "page_url": course_page.url,
            "financial_assistance_form_url": f"{course_page.get_url()}{financial_assistance_page.slug}/",
            "instructors": [],
            "current_price": None,
            "description": bleach.clean(course_page.description, tags=[], strip=True),
            "live": True,
            "length": course_page.length,
            "effort": course_page.effort,
        },
    )
    patched_get_wagtail_src.assert_called_once_with(course_page.feature_image)


def test_serialize_course_page_with_flex_price_with_program_fk_and_parent(
    mocker, fully_configured_wagtail, staff_user, mock_context
):
    """
    Tests course page serialization with Financial Assistance form which has a fk relationship to
    a program, it also has parent-child relationship with program.
    """
    fake_image_src = "http://example.com/my.img"
    mocker.patch("cms.serializers.get_wagtail_img_src", return_value=fake_image_src)

    program = ProgramFactory(page=None)
    program_page = ProgramPageFactory(program=program)
    financial_assistance_form = FlexiblePricingFormFactory(
        selected_program_id=program.id, parent=program_page
    )
    course = CourseFactory(page=None)
    program.add_requirement(course)
    course_page = CoursePageFactory(course=course)

    rf = RequestFactory()
    request = rf.get("/")
    request.user = staff_user

    data = CoursePageSerializer(
        instance=course_page, context=course_page.get_context(request)
    ).data
    assert_drf_json_equal(
        data,
        {
            "feature_image_src": fake_image_src,
            "page_url": course_page.url,
            "financial_assistance_form_url": f"{program_page.get_url()}{financial_assistance_form.slug}/",
            "instructors": [],
            "current_price": None,
            "description": bleach.clean(course_page.description, tags=[], strip=True),
            "live": True,
            "length": course_page.length,
            "effort": course_page.effort,
        },
    )


def test_serialize_course_page_with_flex_price_with_program_fk_no_parent(
    mocker, fully_configured_wagtail, staff_user, mock_context
):
    """
    Tests course page serialization with Financial Assistance form which has a fk relationship to
    a program, but no parent-child relationship with any course or program.
    """
    fake_image_src = "http://example.com/my.img"
    mocker.patch("cms.serializers.get_wagtail_img_src", return_value=fake_image_src)

    program = ProgramFactory(page=None)
    program_page = ProgramPageFactory(program=program)
    financial_assistance_form = FlexiblePricingFormFactory(
        selected_program_id=program.id
    )
    course = CourseFactory(page=None)
    program.add_requirement(course)
    course_page = CoursePageFactory(course=course)

    rf = RequestFactory()
    request = rf.get("/")
    request.user = staff_user

    data = CoursePageSerializer(
        instance=course_page, context=course_page.get_context(request)
    ).data
    assert_drf_json_equal(
        data,
        {
            "feature_image_src": fake_image_src,
            "page_url": course_page.url,
            "financial_assistance_form_url": f"{course_page.get_url()}{financial_assistance_form.slug}/",
            "instructors": [],
            "current_price": None,
            "description": bleach.clean(course_page.description, tags=[], strip=True),
            "live": True,
            "length": course_page.length,
            "effort": course_page.effort,
        },
    )


def test_serialize_course_page_with_flex_price_form_as_program_child(
    mocker, fully_configured_wagtail, staff_user, mock_context
):
    """
    Tests course page serialization with Financial Assistance form which has no fk relationship
    to a course or program, only a parent-child relationship with a program.
    """
    fake_image_src = "http://example.com/my.img"
    mocker.patch("cms.serializers.get_wagtail_img_src", return_value=fake_image_src)

    program = ProgramFactory(page=None)
    program_page = ProgramPageFactory(program=program)
    FlexiblePricingFormFactory(parent=program_page)
    course = CourseFactory(page=None)
    program.add_requirement(course)
    course_page = CoursePageFactory(course=course)

    rf = RequestFactory()
    request = rf.get("/")
    request.user = staff_user
    financial_assistance_page = (
        program_page.get_children().type(FlexiblePricingRequestForm).live().first()
    )
    data = CoursePageSerializer(
        instance=course_page, context=program_page.get_context(request)
    ).data
    assert_drf_json_equal(
        data,
        {
            "feature_image_src": fake_image_src,
            "page_url": course_page.url,
            "financial_assistance_form_url": f"{program_page.get_url()}{financial_assistance_page.slug}/",
            "instructors": [],
            "current_price": None,
            "description": bleach.clean(course_page.description, tags=[], strip=True),
            "live": True,
            "length": course_page.length,
            "effort": course_page.effort,
        },
    )


def test_serialize_course_page_with_flex_price_form_as_child_no_program(
    mocker, fully_configured_wagtail, staff_user, mock_context
):
    """
    Tests course page serialization with Financial Assistance form with a fk relationship with a course
    but no parent-child relationship with a course or program.
    """
    fake_image_src = "http://example.com/my.img"
    mocker.patch("cms.serializers.get_wagtail_img_src", return_value=fake_image_src)

    course = CourseFactory(page=None)
    course_page = CoursePageFactory(course=course)
    financial_assistance_form = FlexiblePricingFormFactory(
        selected_course_id=course.id, parent=course_page
    )

    rf = RequestFactory()
    request = rf.get("/")
    request.user = staff_user

    data = CoursePageSerializer(
        instance=course_page, context=course_page.get_context(request)
    ).data
    assert_drf_json_equal(
        data,
        {
            "feature_image_src": fake_image_src,
            "page_url": course_page.url,
            "financial_assistance_form_url": f"{course_page.get_url()}{financial_assistance_form.slug}/",
            "instructors": [],
            "current_price": None,
            "description": bleach.clean(course_page.description, tags=[], strip=True),
            "live": True,
            "length": course_page.length,
            "effort": course_page.effort,
        },
    )


@pytest.mark.parametrize(
    "own_program_has_form,related_program,related_program_has_form",
    [
        [True, False, False],
        [True, True, False],
        [False, True, False],
        [False, True, True],
        [True, True, True],
    ],
)
def test_serialized_course_finaid_form_url(
    own_program_has_form, related_program, related_program_has_form
):
    """
    Tests the financial assistance form URL returned for a course that's in a
    program that has no financial assistance form and is related to a program
    that does have a financial assistance form. (The course should get the
    form URL for the program that does have the financial assistance form.)
    """

    program1 = ProgramFactory.create()
    course1 = CourseFactory.create()
    program1.add_requirement(course1)

    program2 = ProgramFactory.create()
    course2 = CourseFactory.create()
    program2.add_requirement(course2)

    if related_program:
        program1.add_related_program(program2)

    if own_program_has_form:
        own_fa_page = FlexiblePricingFormFactory.create(
            parent=program1.page, selected_program=program1
        )

        serialized_output = CoursePageSerializer(course1.page).data

        assert own_fa_page.slug in serialized_output["financial_assistance_form_url"]
    else:
        serialized_output = CoursePageSerializer(course1.page).data

        assert serialized_output["financial_assistance_form_url"] == ""

    if related_program_has_form:
        related_fa_page = FlexiblePricingFormFactory.create(
            parent=program2.page, selected_program=program2
        )

        serialized_output = CoursePageSerializer(course1.page).data

        if own_program_has_form:
            assert (
                own_fa_page.slug in serialized_output["financial_assistance_form_url"]
            )
        else:
            assert (
                related_fa_page.slug
                in serialized_output["financial_assistance_form_url"]
            )
