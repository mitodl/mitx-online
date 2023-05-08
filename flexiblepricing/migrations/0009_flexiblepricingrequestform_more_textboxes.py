# Generated by Django 3.2.12 on 2022-05-06 19:11

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("flexiblepricing", "0008_flexiblepricingrequestform_guest_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="flexiblepricingrequestform",
            name="application_approved_text",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="What to show if the user's request has been approved.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="flexiblepricingrequestform",
            name="application_denied_text",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="What to show if the user's request has been denied.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="flexiblepricingrequestform",
            name="application_processing_text",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="What to show if the user's request is being processed.",
                null=True,
            ),
        ),
    ]
