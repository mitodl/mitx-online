# Generated by Django 3.2.15 on 2022-12-14 20:53

import django.db.models.deletion
from django.db import migrations, models

import courses.models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0078_referenceindex"),
        ("courses", "0026_alter_courseruncertificate_certificate_page_revision"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programcertificate",
            name="certificate_page_revision",
            field=models.ForeignKey(
                limit_choices_to=courses.models.limit_to_certificate_pages,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="wagtailcore.revision",
            ),
        ),
    ]
