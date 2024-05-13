# Generated by Django 3.1.12 on 2021-07-19 16:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "position_in_program",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "readable_id",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[\\w\\-+:]+$",
                                "This field is used to produce URL paths. It must contain only characters that match this pattern: [\\w\\-+:]",
                            )
                        ],
                    ),
                ),
                ("live", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ("program", "title"),
            },
        ),
        migrations.CreateModel(
            name="CourseRun",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("courseware_id", models.CharField(max_length=255, unique=True)),
                (
                    "run_tag",
                    models.CharField(
                        help_text="A string that identifies the set of runs that this run belongs to (example: 'R2')",
                        max_length=10,
                    ),
                ),
                (
                    "courseware_url_path",
                    models.CharField(blank=True, max_length=500, null=True),
                ),
                (
                    "start_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "end_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "enrollment_start",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "enrollment_end",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "expiration_date",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        help_text="The date beyond which the learner should not see link to this course run on their dashboard.",
                        null=True,
                    ),
                ),
                ("live", models.BooleanField(default=False)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courseruns",
                        to="courses.course",
                    ),
                ),
            ],
            options={
                "unique_together": {("course", "run_tag")},
            },
        ),
        migrations.CreateModel(
            name="CourseRunEnrollment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "change_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("deferred", "deferred"),
                            ("transferred", "transferred"),
                            ("refunded", "refunded"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="Indicates whether or not this enrollment should be considered active",
                    ),
                ),
                (
                    "edx_enrolled",
                    models.BooleanField(
                        default=False,
                        help_text="Indicates whether or not the request succeeded to enroll via the edX API",
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.courserun",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "run")},
            },
        ),
        migrations.CreateModel(
            name="CourseRunGrade",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "grade",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1.0),
                        ]
                    ),
                ),
                ("letter_grade", models.CharField(blank=True, max_length=6, null=True)),
                ("passed", models.BooleanField(default=False)),
                ("set_by_admin", models.BooleanField(default=False)),
                (
                    "course_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.courserun",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "course_run")},
            },
        ),
        migrations.CreateModel(
            name="CourseTopic",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=128, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Program",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                (
                    "readable_id",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[\\w\\-+:]+$",
                                "This field is used to produce URL paths. It must contain only characters that match this pattern: [\\w\\-+:]",
                            )
                        ],
                    ),
                ),
                ("live", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProgramEnrollment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "change_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("deferred", "deferred"),
                            ("transferred", "transferred"),
                            ("refunded", "refunded"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="Indicates whether or not this enrollment should be considered active",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.program",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "program")},
            },
        ),
        migrations.CreateModel(
            name="ProgramEnrollmentAudit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("data_before", models.JSONField(blank=True, null=True)),
                ("data_after", models.JSONField(blank=True, null=True)),
                (
                    "acting_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.programenrollment",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CourseRunGradeAudit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("data_before", models.JSONField(blank=True, null=True)),
                ("data_after", models.JSONField(blank=True, null=True)),
                (
                    "acting_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "course_run_grade",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="courses.courserungrade",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CourseRunEnrollmentAudit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("data_before", models.JSONField(blank=True, null=True)),
                ("data_after", models.JSONField(blank=True, null=True)),
                (
                    "acting_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="courses.courserunenrollment",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="course",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="courses",
                to="courses.program",
            ),
        ),
        migrations.AddField(
            model_name="course",
            name="topics",
            field=models.ManyToManyField(blank=True, to="courses.CourseTopic"),
        ),
        migrations.CreateModel(
            name="ProgramRun",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "run_tag",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[\\w\\-+:]+$",
                                "This field is used to produce URL paths. It must contain only characters that match this pattern: [\\w\\-+:]",
                            )
                        ],
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "end_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="programruns",
                        to="courses.program",
                    ),
                ),
            ],
            options={
                "unique_together": {("program", "run_tag")},
            },
        ),
    ]
