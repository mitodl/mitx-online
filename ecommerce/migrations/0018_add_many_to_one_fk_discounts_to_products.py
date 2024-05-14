# Generated by Django 3.2.14 on 2022-07-18 15:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0017_add_blank_reason_field"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscountProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "discount",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="ecommerce.discount",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="discounts",
                        to="ecommerce.product",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
