# Generated by Django 2.1.7 on 2019-06-20 19:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("openedx", "0003_add_edx_auth")]

    operations = [
        migrations.AlterField(
            model_name="openedxuser",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="openedx_users",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="openedxapiauth",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="openedx_api_auth",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
