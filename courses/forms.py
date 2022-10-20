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
from courses.serializers import ProgramRequirementTreeSerializer
from courses.widgets import ProgramRequirementsInput


def program_requirements_schema():
    # here, you can create a schema dynamically
    # such as read data from database and populate choices

    courses = Course.objects.live().order_by("title")

    return {
        "title": "Requirements",
        "type": "array",
        "items": {
            "$ref": "#/$defs/node",
            "title": "Section",
            "headerTemplate": "{{ self.data.title }}",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "node_type": {
                            "type": "string",
                            "default": ProgramRequirementNodeType.OPERATOR.value,
                            "options": {
                                "hidden": True,
                            },
                        }
                    },
                },
                "children": {
                    "type": "array",
                    "title": "Requirements",
                    "format": "table",
                    "items": {
                        "title": "Requirement",
                        "$ref": "#/$defs/node",
                        "properties": {
                            "children": {
                                "type": "array",
                                "title": "Requirements",
                                "format": "table",
                                "options": {
                                    "dependencies": {
                                        "data.node_type": ProgramRequirementNodeType.OPERATOR.value,
                                    }
                                },
                                "items": {
                                    "$ref": "#/$defs/node",
                                    "properties": {
                                        "data": {
                                            "properties": {
                                                "node_type": {
                                                    "type": "string",
                                                    "default": ProgramRequirementNodeType.COURSE.value,
                                                    "options": {
                                                        "hidden": True,
                                                    },
                                                }
                                            },
                                        },
                                    },
                                },
                            }
                        },
                    },
                },
            },
        },
        "$defs": {
            "node": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "title": "Details",
                        "propertyOrder": 1,
                        "properties": {
                            "node_type": {
                                "type": "string",
                                "title": "Type",
                                "enum": [
                                    ProgramRequirementNodeType.COURSE.value,
                                    ProgramRequirementNodeType.OPERATOR.value,
                                ],
                                "options": {
                                    "enum_titles": [
                                        ProgramRequirementNodeType.COURSE.label,
                                        ProgramRequirementNodeType.OPERATOR.label,
                                    ],
                                },
                            },
                            "title": {
                                "type": "string",
                                "title": "Title",
                                "default": None,
                                "options": {
                                    "dependencies": {
                                        "node_type": ProgramRequirementNodeType.OPERATOR.value,
                                    }
                                },
                            },
                            "operator": {
                                "type": "string",
                                "title": "Operation",
                                "enum": ProgramRequirement.Operator.values,
                                "default": None,
                                "options": {
                                    "dependencies": {
                                        "node_type": ProgramRequirementNodeType.OPERATOR.value,
                                    },
                                    "enum_titles": ProgramRequirement.Operator.labels
                                },
                            },
                            "operator_value": {
                                "type": "string",
                                "format": "number",
                                "title": "Value",
                                "default": None,
                                "options": {
                                    "dependencies": {
                                        "node_type": ProgramRequirementNodeType.OPERATOR.value,
                                        "operator": ProgramRequirement.Operator.MIN_NUMBER_OF.value,
                                    },
                                },
                            },
                            # course fields
                            "course": {
                                "type": "number",
                                "title": "Course",
                                "default": "undefined",
                                "enum": [course.id for course in courses],
                                "options": {
                                    "dependencies": {
                                        "node_type": ProgramRequirementNodeType.COURSE.value
                                    },
                                    "enum_titles": [course.title for course in courses],
                                },
                            },
                        },
                    }
                },
            },
        },
    }


class ProgramAdminForm(ModelForm):
    """Custom form for handling requirements data"""

    requirements = JSONField(
        widget=ProgramRequirementsInput(schema=program_requirements_schema)
    )

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop("initial", {})
        instance = kwargs.get("instance", None)

        if instance is not None and instance.requirements_root is not None:
            initial["requirements"] = self._serialize_requirements(instance.requirements_root)

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

    def _serialize_requirements(self, root):
        data = ProgramRequirement.dump_bulk(
            parent=root, keep_ids=False
        )[0].get("children", [])

        def _serialize(node):
            return {
                **node,
                "children": [_serialize(child) for child in node.get("children", [])]
            }


        return [_serialize(node) for node in data]

    def clean_requirements(self):
        def _clean(req):
            return {
                **req,
                "data": {
                    **req["data"],
                    "program_id": self.instance.id
                },
                **({
                    "children": [_clean(req) for req in data["children"]]
                } if "children" in req["data"] else {})
            }

        return [_clean(req) for req in self.cleaned_data["requirements"]]

    def save_m2m(self):
        """Save requirements"""
        ProgramRequirement.load_bulk(
            self.cleaned_data["requirements"],
            parent=self.instance.requirements_root
        )

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
        js = (webpack_loader_utils.get_static("requirementsAdmin.js"),)
