# Generated by Django 3.2.15 on 2023-02-14 06:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0029_add_certificate_available_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="position_in_program",
        ),
    ]
