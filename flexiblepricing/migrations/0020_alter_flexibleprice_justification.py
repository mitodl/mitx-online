# Generated by Django 3.2.15 on 2022-09-13 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flexiblepricing", "0019_add_unique_user_courseware_to_flexiblepricing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flexibleprice",
            name="justification",
            field=models.TextField(blank=True, null=True),
        ),
    ]
