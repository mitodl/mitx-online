# Generated by Django 3.2.5 on 2021-12-09 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0007_rename_unenrolled_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="courserunenrollment",
            name="edx_emails_subscription",
            field=models.BooleanField(default=True),
        ),
    ]
