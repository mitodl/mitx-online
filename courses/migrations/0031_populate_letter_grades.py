# Generated by Django 3.2.18 on 2023-06-22 19:54
import datetime

import pytz
from django.db import migrations

from courses.utils import convert_to_letter


def populate_letter_grade(apps, schema_editor):
    """Populate the certificate_available_date from course run's end_date"""
    CourseRunGrade = apps.get_model("courses", "CourseRunGrade")
    grades = CourseRunGrade.objects.filter(
        passed=True,
        letter_grade__contains="Pass",
        course_run__course__program__title__startswith="Data",
        course_run__start_date__lt=datetime.datetime(2022, 9, 1, tzinfo=pytz.UTC),
    )
    for grade in grades:
        grade.letter_grade = convert_to_letter(grade.grade)
        grade.save()


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0030_remove_course_position_in_program"),
    ]

    operations = [
        migrations.RunPython(populate_letter_grade, migrations.RunPython.noop),
    ]
