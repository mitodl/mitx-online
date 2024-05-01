# Generated by Django 3.1.12 on 2021-08-20 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0009_product_faculty_section"),
    ]

    operations = [
        migrations.AddField(
            model_name="coursepage",
            name="video_url",
            field=models.URLField(
                blank=True,
                help_text="URL to the video to be displayed for this program/course. It can be an HLS or Youtube video URL.",
                null=True,
            ),
        ),
    ]
