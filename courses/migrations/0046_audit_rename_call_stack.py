# Generated by Django 3.2.23 on 2024-03-06 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0045_audit_modified_by"),
    ]

    operations = [
        migrations.RenameField(
            model_name="courserunenrollmentaudit",
            old_name="modified_by",
            new_name="call_stack",
        ),
        migrations.RenameField(
            model_name="courserungradeaudit",
            old_name="modified_by",
            new_name="call_stack",
        ),
        migrations.RenameField(
            model_name="programenrollmentaudit",
            old_name="modified_by",
            new_name="call_stack",
        ),
    ]