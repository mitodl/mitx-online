# Generated by Django 4.2 on 2024-09-10 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0055_rename_programrequirement_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='availability',
            field=models.CharField(choices=[('dated', 'dated'), ('anytime', 'anytime')], default='anytime', max_length=255),
        ),
    ]
