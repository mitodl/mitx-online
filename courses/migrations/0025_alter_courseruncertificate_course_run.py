# Generated by Django 3.2.15 on 2022-12-07 10:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0024_add_record_share_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="courseruncertificate",
            name="course_run",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="courseruncertificates",
                to="courses.courserun",
            ),
        ),
    ]
