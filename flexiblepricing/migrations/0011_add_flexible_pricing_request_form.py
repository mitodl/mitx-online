# Generated by Django 3.2.12 on 2022-05-09 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0066_collection_management_permissions"),
        ("wagtailforms", "0004_add_verbose_name_plural"),
        ("wagtailredirects", "0006_redirect_increase_max_length"),
        ("flexiblepricing", "0010_link_flexprice_form_subs_to_requests"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="formfield",
            name="page",
        ),
        migrations.DeleteModel(
            name="FlexiblePricingRequestForm",
        ),
        migrations.DeleteModel(
            name="FormField",
        ),
    ]
