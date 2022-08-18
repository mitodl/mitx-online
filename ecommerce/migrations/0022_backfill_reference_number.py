# Generated by Django 3.2.14 on 2022-08-09 16:25

from django.db import migrations
from ecommerce.constants import REFERENCE_NUMBER_PREFIX
from django.conf import settings
from django.db.models import F, Value
from django.db.models.functions import Concat


def backfill_order_reference_number(apps, schema_editor):
    Order = apps.get_model("ecommerce", "Order")
    Order.objects.filter(reference_number__isnull=True).update(
        reference_number=Concat(
            Value(REFERENCE_NUMBER_PREFIX),
            Value(settings.ENVIRONMENT),
            Value("-"),
            F("id"),
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("ecommerce", "0021_order_reference_number"),
    ]

    operations = [
        migrations.RunPython(
            backfill_order_reference_number, migrations.RunPython.noop
        ),
    ]
