# Generated by Django 3.2.14 on 2022-07-20 07:03

import cms.blocks
from django.db import migrations, models
import django.db.models.deletion
import wagtail.contrib.routable_page.models
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('wagtailcore', '0066_collection_management_permissions'),
        ('cms', '0018_add_country_field_for_flexible_pricing'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtail.contrib.routable_page.models.RoutablePageMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='CertificatePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('product_name', models.CharField(help_text='Specify the course/program name.', max_length=250)),
                ('CEUs', models.CharField(blank=True, help_text='Optional text field for CEU (continuing education unit).', max_length=250, null=True)),
                ('signatories', wagtail.core.fields.StreamField([('signatory', wagtail.core.blocks.PageChooserBlock(page_type=['cms.SignatoryPage'], required=True))], help_text='You can choose upto 5 signatories.')),
                ('overrides', wagtail.core.fields.StreamField([('course_run', wagtail.core.blocks.StructBlock([('readable_id', cms.blocks.CourseRunFieldBlock(help_text='Course run to add the override for')), ('CEUs', wagtail.core.blocks.DecimalBlock(help_text='CEUs to override for this CourseRun, for display on the certificate'))]))], blank=True, help_text='Overrides for specific runs of this Course/Program', validators=[cms.blocks.validate_unique_readable_ids])),
            ],
            options={
                'verbose_name': 'Certificate',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='SignatoryIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='SignatoryPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('name', models.CharField(help_text='Name of the signatory.', max_length=250)),
                ('title_1', models.CharField(blank=True, help_text='Specify signatory first title in organization.', max_length=250, null=True)),
                ('title_2', models.CharField(blank=True, help_text='Specify signatory second title in organization.', max_length=250, null=True)),
                ('organization', models.CharField(blank=True, help_text='Specify the organization of signatory.', max_length=250, null=True)),
                ('signature_image', models.ForeignKey(blank=True, help_text='Signature image size must be at least 150x50 pixels.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'verbose_name': 'Signatory',
            },
            bases=('wagtailcore.page',),
        ),
    ]
