# Generated by Django 3.2.15 on 2022-08-16 19:46

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0022_merge_20220805_1914"),
    ]

    operations = [
        migrations.AddField(
            model_name="flexiblepricingrequestform",
            name="application_approved_no_discount_text",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="What to show if the user's request has been approved, but their discount is zero.",
                null=True,
            ),
        ),
    ]
