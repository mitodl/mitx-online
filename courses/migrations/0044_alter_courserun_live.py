# Generated by Django 3.2.20 on 2023-09-15 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0043_course_program_live_index"),
    ]

    operations = [
        migrations.AlterField(
            model_name="courserun",
            name="live",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
