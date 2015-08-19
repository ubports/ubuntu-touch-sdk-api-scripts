# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_auto_20150819_0908'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalDocsBranch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lp_origin', models.CharField(help_text='Launchpad branch location, ie: lp:snappy/15.04', max_length=200)),
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
    ]
