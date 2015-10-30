# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_auto_20151030_1602'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalDocsBranch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lp_origin', models.CharField(help_text='External branch location, ie: lp:snappy/15.04 or git://github.com/ubuntu-core/snappy', max_length=200)),
                ('docs_namespace', models.CharField(help_text='Path alias we want to use for the docs, ie "snappy/guides/15.04" or "snappy/guides/latest", etc.', max_length=120)),
                ('index_doc', models.CharField(help_text='File name of doc to be used as index document, ie "intro.md"', max_length=120, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RawHtml',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('body', models.TextField(verbose_name='body')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='SEOExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keywords', models.CharField(max_length=256)),
                ('extended_object', models.OneToOneField(editable=False, to='cms.Title')),
                ('public_extension', models.OneToOneField(related_name='draft_extension', null=True, editable=False, to='developer_portal.SEOExtension')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
