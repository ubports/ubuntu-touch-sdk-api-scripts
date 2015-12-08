# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('developer_portal', '0002_rework_importer'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedArticle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_import', models.DateTimeField(help_text='Datetime of last import.', verbose_name='Datetime')),
                ('branch', models.ForeignKey(to='developer_portal.ExternalDocsBranch')),
                ('page', models.ForeignKey(to='cms.Page')),
            ],
        ),
    ]
