# Generated by Django 3.2.18 on 2023-03-17 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("openedx", "0004_add_openedx_related_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="openedxuser",
            name="has_been_synced",
            field=models.BooleanField(
                default=False,
                help_text="Indicates whether a corresponding user has been created on the openedx platform",
            ),
        ),
    ]
