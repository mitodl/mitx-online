# Generated by Django 3.1.12 on 2021-10-15 17:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0006_enrollments_related"),
    ]

    operations = [
        migrations.AlterField(
            model_name="courserunenrollment",
            name="change_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("deferred", "deferred"),
                    ("transferred", "transferred"),
                    ("refunded", "refunded"),
                    ("unenrolled", "unenrolled"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="programenrollment",
            name="change_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("deferred", "deferred"),
                    ("transferred", "transferred"),
                    ("refunded", "refunded"),
                    ("unenrolled", "unenrolled"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
