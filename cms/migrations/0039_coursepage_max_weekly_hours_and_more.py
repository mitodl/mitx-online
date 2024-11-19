# Generated by Django 4.2.16 on 2024-11-18 17:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0038_alter_instructorpagelink_linked_instructor_page"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursepage",
            name="max_weekly_hours",
            field=models.CharField(
                default="",
                help_text="The maximum number of hours per week required to complete the course.",
                max_length=5,
            ),
        ),
        migrations.AddField(
            model_name="coursepage",
            name="min_weekly_hours",
            field=models.CharField(
                default="",
                help_text="The minimum number of hours per week required to complete the course.",
                max_length=5,
            ),
        ),
        migrations.AddField(
            model_name="programpage",
            name="max_weekly_hours",
            field=models.CharField(
                default="",
                help_text="The maximum number of hours per week required to complete the course.",
                max_length=5,
            ),
        ),
        migrations.AddField(
            model_name="programpage",
            name="min_weekly_hours",
            field=models.CharField(
                default="",
                help_text="The minimum number of hours per week required to complete the course.",
                max_length=5,
            ),
        ),
    ]
