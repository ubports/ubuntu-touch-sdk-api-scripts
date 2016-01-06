# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
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
