# Generated by Django 3.2.14 on 2022-07-28 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0018_add_country_field_for_flexible_pricing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flexiblepricingrequestform',
            name='thank_you_text',
        ),
    ]
