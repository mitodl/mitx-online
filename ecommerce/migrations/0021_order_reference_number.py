# Generated by Django 3.2.14 on 2022-08-09 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0020_product_unique_object_id_validated"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="reference_number",
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
