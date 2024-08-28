# Generated by Django 3.2.25 on 2024-07-31 16:42

from django.db import migrations


def deactivate_program_enrollments(apps, schema_editor):
    """Deactivate all Enrollments for this not yet live program"""
    ProgramEnrollments = apps.get_model("courses", "ProgramEnrollment")
    enrollments = ProgramEnrollments.objects.filter(
        program__readable_id="program-v1:MITxT+18.01x"
    )
    for enrollment in enrollments:
        enrollment.active = False
        enrollment.save()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0052_add_program_availability"),
    ]

    operations = [
        migrations.RunPython(deactivate_program_enrollments, migrations.RunPython.noop),
    ]
