# Generated by Django 3.2.23 on 2024-05-15 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0050_make_department_slug_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursesTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtopics', to='courses.coursestopic')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]