# Generated by Django 3.2.12 on 2022-02-25 21:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("ecommerce", "0010_add_basket_discount_20220114_2107"),
    ]

    operations = [
        migrations.AddField(
            model_name="line",
            name="purchased_content_type",
            field=models.ForeignKey(
                limit_choices_to=models.Q(
                    models.Q(("app_label", "courses"), ("model", "courserun")),
                    models.Q(("app_label", "courses"), ("model", "programrun")),
                    _connector="OR",
                ),
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="line",
            name="purchased_object_id",
            field=models.PositiveIntegerField(null=True),
        ),
    ]
