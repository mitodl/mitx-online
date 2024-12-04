# Generated by Django 4.2.16 on 2024-12-03 18:25

import re

from django.db import migrations


def populate_max_min_weeks_fields(apps, schema_editor):
    CoursePage = apps.get_model("cms", "CoursePage")
    for course_page in CoursePage.objects.all():
        if course_page.length:
            duration_nums = re.findall(r"\d+", course_page.length)
            if len(duration_nums) > 0:
                course_page.max_weeks = duration_nums[0]
                course_page.min_weeks = duration_nums[0]
                course_page.save()

    ProgramPage = apps.get_model("cms", "ProgramPage")
    for program_page in ProgramPage.objects.all():
        if program_page.length and program_page.max_weeks is None:
            duration_string = re.findall(
                r"\d+[\s-]*[\d+\s]*week", program_page.length.lower()
            )
            if duration_string:
                duration_nums = re.findall(r"\d+", duration_string[0])
            else:
                duration_string = re.findall(
                    r"\d+[\s-]*[\d+\s]*month", program_page.length.lower()
                )
                duration_nums_in_month = re.findall(r"\d+", duration_string[0])
                duration_nums = [num * 4 for num in duration_nums_in_month]
            program_page.min_weeks = duration_nums[0]
            program_page.max_weeks = (
                duration_nums[1] if len(duration_nums) > 1 else duration_nums[0]
            )
            program_page.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0040_coursepage_max_weeks_coursepage_min_weeks_and_more"),
    ]

    operations = [
        migrations.RunPython(
            populate_max_min_weeks_fields, reverse_code=migrations.RunPython.noop
        ),
    ]
