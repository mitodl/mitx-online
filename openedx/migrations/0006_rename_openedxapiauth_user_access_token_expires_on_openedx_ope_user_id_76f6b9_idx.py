# Generated by Django 4.2 on 2024-09-05 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openedx', '0005_alter_openedxuser_has_been_synced'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='openedxapiauth',
            new_name='openedx_ope_user_id_76f6b9_idx',
            old_fields=('user', 'access_token_expires_on'),
        ),
    ]
