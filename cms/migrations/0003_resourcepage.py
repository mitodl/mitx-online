# Generated by Django 3.1.12 on 2021-07-30 12:36

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0062_comment_models_and_pagesubscription"),
        ("wagtailimages", "0023_add_choose_permissions"),
        ("cms", "0002_course_page"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourcePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "content",
                    wagtail.core.fields.StreamField(
                        [
                            (
                                "content",
                                wagtail.core.blocks.StructBlock(
                                    [
                                        (
                                            "heading",
                                            wagtail.core.blocks.CharBlock(
                                                max_length=100
                                            ),
                                        ),
                                        ("detail", wagtail.core.blocks.RichTextBlock()),
                                    ]
                                ),
                            )
                        ],
                        help_text="Enter details of content.",
                    ),
                ),
                (
                    "header_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Upload a header image that will render in the resource page. (The recommended dimensions for the image are 1920x300)",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
