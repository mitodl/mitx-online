# Generated by Django 3.2.18 on 2023-05-22 14:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0033_remove_discount_for_flexible_pricing"),
    ]

    operations = [
        migrations.AddField(
            model_name="discount",
            name="is_bulk",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="discount",
            name="discount_code",
            field=models.CharField(max_length=100),
        ),
    ]