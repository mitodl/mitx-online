# Generated by Django 3.2.15 on 2023-02-09 08:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0030_alter_discount_for_flexible_pricing"),
    ]

    operations = [
        migrations.AddField(
            model_name="discount",
            name="payment_type",
            field=models.CharField(
                choices=[
                    ("marketing", "marketing"),
                    ("sales", "sales"),
                    ("financial-assistance", "financial-assistance"),
                    ("customer-support", "customer-support"),
                    ("staff", "staff"),
                    ("legacy", "legacy"),
                ],
                max_length=30,
                null=True,
            ),
        ),
    ]
