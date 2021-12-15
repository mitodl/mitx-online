# Generated by Django 3.2.10 on 2022-01-05 17:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import ecommerce.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reversion", "0002_add_index_on_version_for_content_type_and_db"),
        ("ecommerce", "0007_update_discount_choice_fields_20220103_1926"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
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
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("pending", "Pending"),
                            ("fulfilled", "Fulfilled"),
                            ("canceled", "Canceled"),
                            ("refunded", "Refunded"),
                        ],
                        default="pending",
                        max_length=50,
                    ),
                ),
                (
                    "total_price_paid",
                    models.DecimalField(decimal_places=5, max_digits=20),
                ),
                (
                    "purchaser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="product",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="Controls visibility of the product in the app.",
            ),
        ),
        migrations.CreateModel(
            name="Transaction",
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
                ("amount", models.DecimalField(decimal_places=5, max_digits=20)),
                ("data", models.JSONField()),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="ecommerce.order",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Line",
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
                ("quantity", models.PositiveIntegerField()),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="ecommerce.order",
                    ),
                ),
                (
                    "product_version",
                    models.ForeignKey(
                        limit_choices_to=ecommerce.models.Line._order_line_product_versions,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reversion.version",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CanceledOrder",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("ecommerce.order",),
        ),
        migrations.CreateModel(
            name="FulfilledOrder",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("ecommerce.order",),
        ),
        migrations.CreateModel(
            name="PendingOrder",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("ecommerce.order",),
        ),
        migrations.CreateModel(
            name="RefundedOrder",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("ecommerce.order",),
        ),
    ]
