from datetime import timedelta

import pytest
from django.utils.timezone import now

from cms.factories import CoursePageFactory
from cms.serializers import ProgramPageSerializer
from courses.factories import (  # noqa: F401
    CourseRunFactory,
    program_with_empty_requirements,
)
from courses.models import CoursesTopic, Department
from courses.serializers.v1.departments import DepartmentSerializer
from courses.serializers.v2.programs import (
    ProgramRequirementTreeSerializer,
    ProgramSerializer,
)
from main.test_utils import assert_drf_json_equal

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize("remove_tree", [True, False])
@pytest.mark.parametrize(
    "certificate_type", ["MicroMasters Credential", "Certificate of Completion"]
)
@pytest.mark.parametrize("prerequisites", ["program prerequisites", None, ""])
def test_serialize_program(
    mock_context,
    remove_tree,
    certificate_type,
    prerequisites,
    program_with_empty_requirements,  # noqa: F811
):
    """Test Program serialization"""
    if certificate_type == "MicroMasters Credential":
        program_with_empty_requirements.program_type = "MicroMasters®"
        program_with_empty_requirements.save()

    required_prerequisites = False
    if prerequisites is not None:
        program_with_empty_requirements.page.prerequisites = prerequisites
    if prerequisites != "":
        required_prerequisites = True

    run1 = CourseRunFactory.create(
        course__page=None,
        start_date=now() + timedelta(hours=1),
    )
    course1 = run1.course
    CoursePageFactory.create(course=run1.course)
    run2 = CourseRunFactory.create(
        course__page=None,
        start_date=now() + timedelta(hours=2),
    )
    course2 = run2.course
    CoursePageFactory.create(course=run2.course)

    formatted_reqs = {"required": [], "electives": []}

    topics = []
    if not remove_tree:
        program_with_empty_requirements.add_requirement(course1)
        program_with_empty_requirements.add_requirement(course2)
        formatted_reqs["required"] = [
            course.id for course in program_with_empty_requirements.required_courses
        ]
        formatted_reqs["electives"] = [
            course.id for course in program_with_empty_requirements.elective_courses
        ]
        topics = [CoursesTopic.objects.create(name=f"topic{num}") for num in range(3)]
        course1.page.topics.set([topics[0], topics[1]])
        course2.page.topics.set([topics[1], topics[2]])
        course1.page.save()
        course2.page.save()
    program_department = Department.objects.create(name="Math")
    program_with_empty_requirements.departments.add(program_department)

    data = ProgramSerializer(
        instance=program_with_empty_requirements, context=mock_context
    ).data

    assert_drf_json_equal(
        data,
        {
            "title": program_with_empty_requirements.title,
            "readable_id": program_with_empty_requirements.readable_id,
            "id": program_with_empty_requirements.id,
            "courses": [course.id for course in [course1, course2]]
            if not remove_tree
            else [],
            "requirements": formatted_reqs,
            "req_tree": ProgramRequirementTreeSerializer(
                program_with_empty_requirements.requirements_root
            ).data,
            "page": ProgramPageSerializer(program_with_empty_requirements.page).data,
            "program_type": program_with_empty_requirements.program_type,
            "certificate_type": certificate_type,
            "departments": [DepartmentSerializer(program_department).data],
            "live": True,
            "topics": [{"name": topic.name} for topic in topics],
            "availability": "anytime",
            "start_date": program_with_empty_requirements.start_date,
            "end_date": program_with_empty_requirements.end_date,
            "enrollment_start": program_with_empty_requirements.enrollment_start,
            "enrollment_end": program_with_empty_requirements.enrollment_end,
            "required_prerequisites": required_prerequisites,
            "duration": program_with_empty_requirements.page.length,
            "time_commitment": program_with_empty_requirements.page.effort,
            "max_weekly_hours": program_with_empty_requirements.page.max_weekly_hours,
            "min_weekly_hours": program_with_empty_requirements.page.min_weekly_hours,
        },
    )
