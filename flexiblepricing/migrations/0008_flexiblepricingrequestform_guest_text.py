# Generated by Django 3.2.12 on 2022-05-06 18:42

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("flexiblepricing", "0007_add_custom_flex_price_submission"),
    ]

    operations = [
        migrations.AddField(
            model_name="flexiblepricingrequestform",
            name="guest_text",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="What to show if the user isn't logged in.",
                null=True,
            ),
        ),
    ]
