# Generated by Django 4.2.16 on 2024-12-03 01:26

from django.db import migrations
import parsedatetime as pdt

def populate_max_min_weeks_fields(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    cal = pdt.Calendar()
    for course in Course.objects.all():
        duration = course.page.duration
        course.max_weeks = course.max_weeks + 1
        course.min_weeks = course.min_weeks - 1

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0057_alter_program_end_date_alter_program_start_date'),
    ]

    operations = [
        migrations.RunPython(populate_max_min_weeks_fields, reverse_code=migrations.RunPython.noop),
    ]
