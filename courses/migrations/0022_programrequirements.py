# Generated by Django 3.2.15 on 2022-10-17 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0021_programrequirements"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="programrequirement",
            name="courses_programrequirement_node_check",
        ),
        migrations.AddField(
            model_name="programrequirement",
            name="node_type",
            field=models.CharField(
                choices=[
                    ("program_root", "Program Root"),
                    ("operator", "Operator"),
                    ("course", "Course"),
                ],
                max_length=12,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="programrequirement",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("course__isnull", True),
                        ("depth", 1),
                        ("node_type", "program_root"),
                        ("operator__isnull", True),
                        ("operator_value__isnull", True),
                    ),
                    models.Q(
                        ("course__isnull", True),
                        ("depth__gt", 1),
                        ("node_type", "operator"),
                        ("operator__isnull", False),
                    ),
                    models.Q(
                        ("course__isnull", False),
                        ("depth__gt", 1),
                        ("node_type", "course"),
                        ("operator__isnull", True),
                        ("operator_value__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="courses_programrequirement_node_check",
            ),
        ),
    ]
