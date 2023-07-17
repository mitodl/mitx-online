# Generated by Django 3.2.18 on 2023-07-17 12:19
from django.db import migrations


def convert_to_letter(grade):
    """Convert a decimal number to letter grade"""
    if grade >= 0.825:
        return "A"
    elif grade >= 0.65:
        return "B"
    elif grade >= 0.55:
        return "C"
    elif grade >= 0.50:
        return "D"
    else:
        return "F"


def populate_letter_grade(apps, schema_editor):
    """Populate letter grades for DEDP courses for 3T2022 semester"""
    CourseRunGrade = apps.get_model("courses", "CourseRunGrade")
    course_run_ids = [
        "course-v1:MITxT+14.100x+3T2022",
        "course-v1:MITxT+14.750x+3T2022",
        "course-v1:MITxT+JPAL102x+3T2022",
        "course-v1:MITxT+14.73x+3T2022",
        "course-v1:MITxT+14.310x+3T2022",
    ]

    grades = CourseRunGrade.objects.filter(
        passed=True,
        letter_grade__contains="Pass",
        course_run__courseware_id__in=course_run_ids,
    )
    for grade in grades:
        grade.letter_grade = convert_to_letter(grade.grade)
        grade.set_by_admin = True
        grade.save()


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0037_update_programrequirements_add_elective_flag"),
    ]

    operations = [
        migrations.RunPython(populate_letter_grade, migrations.RunPython.noop),
    ]
