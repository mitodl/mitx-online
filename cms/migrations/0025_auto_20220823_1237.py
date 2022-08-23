# Generated by Django 3.2.15 on 2022-08-23 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('cms', '0024_merge_20220817_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursepage',
            name='feature_image',
            field=models.ForeignKey(blank=True, help_text='Image that will be used where the course is featured or linked. (The recommended dimensions for the image are 375x244)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
        migrations.AlterField(
            model_name='programpage',
            name='feature_image',
            field=models.ForeignKey(blank=True, help_text='Image that will be used where the course is featured or linked. (The recommended dimensions for the image are 375x244)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
    ]
