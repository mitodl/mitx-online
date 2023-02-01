# Generated by Django 3.2.15 on 2023-02-01 12:48

from django.db import migrations

from ecommerce.constants import PAYMENT_TYPE_FINANCIAL_ASSISTANCE


def backfill_payment_type_for_financial_assistance(apps, schema_editor):
    discount = apps.get_model("ecommerce", "Discount")
    discount.objects.filter(for_flexible_pricing=True).update(
        payment_type=PAYMENT_TYPE_FINANCIAL_ASSISTANCE
    )


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0031_discount_payment_type"),
    ]

    operations = [
        migrations.RunPython(
            backfill_payment_type_for_financial_assistance, migrations.RunPython.noop
        ),
    ]
