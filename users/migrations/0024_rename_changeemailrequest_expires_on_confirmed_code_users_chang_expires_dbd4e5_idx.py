# Generated by Django 4.2 on 2024-09-05 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_user_hubspot_sync_datetime'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='changeemailrequest',
            new_name='users_chang_expires_dbd4e5_idx',
            old_fields=('expires_on', 'confirmed', 'code'),
        ),
    ]
