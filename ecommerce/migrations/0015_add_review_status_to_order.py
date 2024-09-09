# Generated by Django 3.2.12 on 2022-03-15 13:49
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0014_add_transaction_type_field"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReviewOrder",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("ecommerce.order",),
        ),
        migrations.AlterField(
            model_name="order",
            name="state",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("fulfilled", "Fulfilled"),
                    ("canceled", "Canceled"),
                    ("declined", "Declined"),
                    ("errored", "Errored"),
                    ("refunded", "Refunded"),
                    ("review", "Review"),
                    ("partially_refunded", "Partially Refunded"),
                ],
                default="pending",
                max_length=50,
            ),
        ),
    ]
