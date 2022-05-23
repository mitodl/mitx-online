# Generated by Django 3.2.13 on 2022-06-01 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0015_add_review_status_to_order"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("flexiblepricing", "0014_alter_currencyexchangerate_exchange_rate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="flexibleprice",
            name="course",
        ),
        migrations.AddField(
            model_name="flexibleprice",
            name="courseware_content_type",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="flexibleprice",
            name="courseware_object_id",
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="FlexiblePriceTier",
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
                ("courseware_object_id", models.PositiveIntegerField()),
                ("current", models.BooleanField(default=False)),
                ("income_threshold_usd", models.FloatField()),
                (
                    "courseware_content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "discount",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="flexible_price_tiers",
                        to="ecommerce.discount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="flexibleprice",
            name="tier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="flexiblepricing.flexiblepricetier",
            ),
        ),
    ]
