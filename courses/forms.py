from django.db.models import F
from django.forms import ModelForm
from django.forms.fields import JSONField
from webpack_loader import utils as webpack_loader_utils

from courses.models import (
    Course,
    Program,
    ProgramRequirement,
    ProgramRequirementNodeType,
)
from courses.widgets import ProgramRequirementsInput


def program_requirements_schema():
    # here, you can create a schema dynamically
    # such as read data from database and populate choices

    courses = Course.objects.live().order_by("title")
    return {
        "title": "Requirements",
        "type": "array",
        "items": {
            "$ref": "#/$defs/operator",
            "headerTemplate": "{{ self.data.title }}",
            "properties": {
                "children": {
                    "type": "array",
                    "title": "Requirements",
                    "items": {
                        "title": "Requirement",
                        "properties": {
                            "node_type": {
                                "type": "string",
                                "title": "Type",
                                "enum": [
                                    ProgramRequirementNodeType.OPERATOR.value,
                                    ProgramRequirementNodeType.COURSE.value,
                                ],
                            }
                        },
                        "oneOf": [
                            {
                                "title": "Course",
                                "$ref": "#/$defs/course",
                            },
                            {
                                "title": "Operator",
                                "$ref": "#/$defs/operator",
                                "properties": {
                                    "children": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/$defs/course",
                                        },
                                    }
                                },
                            },
                        ],
                    },
                }
            },
        },
        "$defs": {
            "course": {
                "type": "object",
                "properties": {
                    "node_type": {
                        "const": ProgramRequirementNodeType.COURSE.value
                    },
                    "course_id": {
                        "type": "number",
                        "title": "Course",
                        "enumSource": [{
                            "value": course.id,
                            "title": course.title,
                        } for course in courses],
                    }
                },
            },
            "operator": {
                "type": "object",
                "properties": {
                    "node_type": {
                        "const": ProgramRequirementNodeType.COURSE.value
                    },
                    "title": {"type": "string", "title": "Title"},
                    "operator": {
                        "type": "string",
                        "title": "Operation",
                        "enum": ProgramRequirement.Operator.values,
                    },
                    "operator_value": {
                        "type": "string",
                        "format": "number",
                        "title": "Value",
                        "options": {
                            "dependencies": {
                                "operator": ProgramRequirement.Operator.MIN_NUMBER_OF.value
                            }
                        },
                    }
                },
            },
        },
    }
    # return {
    #     "title": "Requirements",
    #     "type": "array",
    #     "items": {
    #         "$ref": "#/$defs/operator",
    #         "headerTemplate": "{{ self.data.title }}",
    #         "properties": {
    #             "children": {
    #                 "type": "array",
    #                 "title": "Requirements",
    #                 "items": {
    #                     "title": "Requirement",
    #                     "properties": {
    #                         "data": {
    #                             "type": "object",
    #                             "properties": {
    #                                 "node_type": {
    #                                     "type": "string",
    #                                     "title": "Type",
    #                                     "enum": [
    #                                         ProgramRequirementNodeType.OPERATOR.value,
    #                                         ProgramRequirementNodeType.COURSE.value,
    #                                     ],
    #                                 }
    #                             },
    #                         }
    #                     },
    #                     "oneOf": [
    #                         {
    #                             "title": "Course",
    #                             "$ref": "#/$defs/course",
    #                         },
    #                         {
    #                             "title": "Operator",
    #                             "$ref": "#/$defs/operator",
    #                             "properties": {
    #                                 "children": {
    #                                     "type": "array",
    #                                     "items": {
    #                                         "$ref": "#/$defs/course",
    #                                     },
    #                                 }
    #                             },
    #                         },
    #                     ],
    #                 },
    #             }
    #         },
    #     },
    #     "$defs": {
    #         "course": {
    #             "type": "object",
    #             "properties": {
    #                 "data": {
    #                     "type": "object",
    #                     "propertyOrder": 1,
    #                     "properties": {
    #                         "node_type": {
    #                             "const": ProgramRequirementNodeType.COURSE.value
    #                         },
    #                         "course_id": {
    #                             "type": "number",
    #                             "title": "Course",
    #                             "enumSource": [{
    #                                 "value": course.id,
    #                                 "title": course.title,
    #                             } for course in courses],
    #                         }
    #                     },
    #                 }
    #             },
    #         },
    #         "operator": {
    #             "type": "object",
    #             "properties": {
    #                 "data": {
    #                     "title": "Details",
    #                     "type": "object",
    #                     "propertyOrder": 1,
    #                     "properties": {
    #                         "node_type": {
    #                             "const": ProgramRequirementNodeType.COURSE.value
    #                         },
    #                         "title": {"type": "string", "title": "Title"},
    #                         "operator": {
    #                             "type": "string",
    #                             "title": "Operation",
    #                             "enum": ProgramRequirement.Operator.values,
    #                         },
    #                         "operator_value": {
    #                             "type": "string",
    #                             "format": "number",
    #                             "title": "Value",
    #                             "options": {
    #                                 "dependencies": {
    #                                     "operator": ProgramRequirement.Operator.MIN_NUMBER_OF.value
    #                                 }
    #                             },
    #                         },
    #                     },
    #                 }
    #             },
    #         },
    #     },
    # }


class ProgramAdminForm(ModelForm):
    """Custom form for handling requirements data"""

    requirements = JSONField(
        widget=ProgramRequirementsInput(schema=program_requirements_schema)
    )

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop("initial", {})
        instance = kwargs.get("instance", None)

        if instance is not None and instance.requirements_root is not None:
            initial["requirements"] = self.serialize_requirements(instance.requirements_root)

        if not initial.get("requirements", None):
            initial["requirements"] = [
                {
                    "data": {
                        "node_type": ProgramRequirementNodeType.OPERATOR.value,
                        "title": "Required Courses",
                        "operator": ProgramRequirement.Operator.ALL_OF.value,
                    },
                    "children": [],
                },
                {
                    "data": {
                        "node_type": ProgramRequirementNodeType.OPERATOR.value,
                        "title": "Elective Courses",
                        "operator": ProgramRequirement.Operator.MIN_NUMBER_OF.value,
                        "operator_value": 1,
                    },
                    "children": [],
                },
            ]

        super().__init__(*args, initial=initial, **kwargs)

    def serialize_requirements(self, root):
        tree = ProgramRequirement.dump_bulk(
            parent=root, keep_ids=False
        )
            
        sections = tree[0].get("children", [])

        def _serialize(nodes):
            for node in nodes:
                data = node["data"]
                node_type = data["node_type"]
                if node_type == ProgramRequirementNodeType.OPERATOR.value:
                    yield {
                        "data": {
                            "title": data["title"],
                            "operator": data["operator"],
                            "operator_value": data["operator_value"],
                        },
                        "children": list(_serialize(data.get("children", []))),
                    }
                elif node_type == ProgramRequirementNodeType.COURSE.value:
                    yield {
                        "data": {
                            "node_type": data["node_type"],
                            "course_id": data["course_id"],
                        }
                    }

        return list(_serialize(sections))

    class Meta:
        model = Program
        fields = [
            "title",
            "readable_id",
            "live",
            "requirements",
        ]

    class Media:
        css = {
            "all": (
                "css/vendor/spectre-icons.min.css",
                "css/admin/requirements.css",
            )
        }
        js = (
            webpack_loader_utils.get_static("requirementsAdmin.js"),
            # 'js/admin/requirements.js',
        )
