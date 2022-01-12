# Generated by Django 3.2.10 on 2022-01-12 19:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0008_add_order_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basketitem',
            name='basket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='basket_items', to='ecommerce.basket'),
        ),
        migrations.AlterField(
            model_name='basketitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
