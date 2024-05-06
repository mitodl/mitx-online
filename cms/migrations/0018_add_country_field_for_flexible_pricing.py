# Generated by Django 3.2.12 on 2022-05-09 16:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0017_add_flexible_pricing_request_form"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formfield",
            name="field_type",
            field=models.CharField(
                choices=[
                    ("singleline", "Single line text"),
                    ("multiline", "Multi-line text"),
                    ("email", "Email"),
                    ("number", "Number"),
                    ("url", "URL"),
                    ("checkbox", "Checkbox"),
                    ("checkboxes", "Checkboxes"),
                    ("dropdown", "Drop down"),
                    ("multiselect", "Multiple select"),
                    ("radio", "Radio buttons"),
                    ("date", "Date"),
                    ("datetime", "Date/time"),
                    ("hidden", "Hidden field"),
                    ("country", "Country"),
                ],
                max_length=20,
                verbose_name="Field Type",
            ),
        ),
    ]
