# Generated by Django 3.2.18 on 2023-05-09 15:31

import cms.blocks
from django.db import migrations, models
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0026_certificate_index_page_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="certificatepage",
            name="overrides",
            field=wagtail.fields.StreamField(
                [
                    (
                        "course_run",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "readable_id",
                                    cms.blocks.CourseRunFieldBlock(
                                        help_text="Course run to add the override for"
                                    ),
                                ),
                                (
                                    "CEUs",
                                    wagtail.blocks.DecimalBlock(
                                        help_text="CEUs to override for this CourseRun, for display on the certificate"
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                help_text="Overrides for specific runs of this Course/Program",
                use_json_field=True,
                validators=[cms.blocks.validate_unique_readable_ids],
            ),
        ),
        migrations.AlterField(
            model_name="certificatepage",
            name="signatories",
            field=wagtail.fields.StreamField(
                [
                    (
                        "signatory",
                        wagtail.blocks.PageChooserBlock(
                            page_type=["cms.SignatoryPage"], required=True
                        ),
                    )
                ],
                help_text="You can choose upto 5 signatories.",
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="faculty_members",
            field=wagtail.fields.StreamField(
                [
                    (
                        "faculty_member",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "name",
                                    wagtail.blocks.CharBlock(
                                        help_text="Name of the faculty member.",
                                        max_length=100,
                                    ),
                                ),
                                (
                                    "image",
                                    wagtail.images.blocks.ImageChooserBlock(
                                        help_text="Profile image size must be at least 300x300 pixels."
                                    ),
                                ),
                                (
                                    "description",
                                    wagtail.blocks.RichTextBlock(
                                        help_text="A brief description about the faculty member."
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                help_text="The faculty members to display on this page",
                null=True,
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="coursepage",
            name="price",
            field=wagtail.fields.StreamField(
                [
                    (
                        "price_details",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "text",
                                    wagtail.blocks.CharBlock(
                                        help="Displayed over the product detail page under the price tile.",
                                        max_length=150,
                                    ),
                                ),
                                (
                                    "link",
                                    wagtail.blocks.URLBlock(
                                        help="Specify the URL to redirect the user for the product's price details page.",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                help_text="Specify the product price details.",
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="formfield",
            name="choices",
            field=models.TextField(
                blank=True,
                help_text="Comma or new line separated list of choices. Only applicable in checkboxes, radio and dropdown.",
                verbose_name="choices",
            ),
        ),
        migrations.AlterField(
            model_name="formfield",
            name="default_value",
            field=models.TextField(
                blank=True,
                help_text="Default value. Comma or new line separated values supported for checkboxes.",
                verbose_name="default value",
            ),
        ),
        migrations.AlterField(
            model_name="programpage",
            name="faculty_members",
            field=wagtail.fields.StreamField(
                [
                    (
                        "faculty_member",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "name",
                                    wagtail.blocks.CharBlock(
                                        help_text="Name of the faculty member.",
                                        max_length=100,
                                    ),
                                ),
                                (
                                    "image",
                                    wagtail.images.blocks.ImageChooserBlock(
                                        help_text="Profile image size must be at least 300x300 pixels."
                                    ),
                                ),
                                (
                                    "description",
                                    wagtail.blocks.RichTextBlock(
                                        help_text="A brief description about the faculty member."
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                help_text="The faculty members to display on this page",
                null=True,
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="programpage",
            name="price",
            field=wagtail.fields.StreamField(
                [
                    (
                        "price_details",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "text",
                                    wagtail.blocks.CharBlock(
                                        help="Displayed over the product detail page under the price tile.",
                                        max_length=150,
                                    ),
                                ),
                                (
                                    "link",
                                    wagtail.blocks.URLBlock(
                                        help="Specify the URL to redirect the user for the product's price details page.",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                help_text="Specify the product price details.",
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="resourcepage",
            name="content",
            field=wagtail.fields.StreamField(
                [
                    (
                        "content",
                        wagtail.blocks.StructBlock(
                            [
                                ("heading", wagtail.blocks.CharBlock(max_length=100)),
                                ("detail", wagtail.blocks.RichTextBlock()),
                            ]
                        ),
                    )
                ],
                help_text="Enter details of content.",
                use_json_field=True,
            ),
        ),
    ]
