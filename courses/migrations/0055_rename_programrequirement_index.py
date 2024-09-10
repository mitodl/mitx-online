# Generated by Django 4.2 on 2024-09-10 17:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0054_add_program_availability"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="programrequirement",
            new_name="courses_pro_course__fdcdb6_idx",
            old_fields=("course", "program"),
        ),
        migrations.RenameIndex(
            model_name="programrequirement",
            new_name="courses_pro_program_c8ff7c_idx",
            old_fields=("program", "course"),
        ),
    ]
