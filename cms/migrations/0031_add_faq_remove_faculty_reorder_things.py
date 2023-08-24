# Generated by Django 3.2.18 on 2023-07-31 14:40

import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0030_move_instructor_short_bios_to_long"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="coursepage",
            name="faculty_members",
        ),
        migrations.RemoveField(
            model_name="programpage",
            name="faculty_members",
        ),
        migrations.AddField(
            model_name="coursepage",
            name="faq_url",
            field=models.URLField(
                blank=True,
                help_text="URL a relevant FAQ page or entry for the course/program.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="programpage",
            name="faq_url",
            field=models.URLField(
                blank=True,
                help_text="URL a relevant FAQ page or entry for the course/program.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="about",
            field=wagtail.fields.RichTextField(
                blank=True, help_text="Details about this course/program.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="description",
            field=wagtail.fields.RichTextField(
                help_text="The description shown on the home page and product page."
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="prerequisites",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="A short description indicating prerequisites of this course/program.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="video_url",
            field=models.URLField(
                blank=True,
                help_text="URL to the video to be displayed for this course/program. It can be an HLS or Youtube video URL.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="programpage",
            name="about",
            field=wagtail.fields.RichTextField(
                blank=True, help_text="Details about this course/program.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="programpage",
            name="description",
            field=wagtail.fields.RichTextField(
                help_text="The description shown on the home page and product page."
            ),
        ),
        migrations.AlterField(
            model_name="programpage",
            name="prerequisites",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="A short description indicating prerequisites of this course/program.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="programpage",
            name="video_url",
            field=models.URLField(
                blank=True,
                help_text="URL to the video to be displayed for this course/program. It can be an HLS or Youtube video URL.",
                null=True,
            ),
        ),
    ]
