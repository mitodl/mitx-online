# Generated by Django 3.2.18 on 2023-06-14 16:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0030_remove_course_position_in_program"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="course",
            options={},
        ),
        migrations.RemoveField(
            model_name="course",
            name="program",
        ),
    ]
