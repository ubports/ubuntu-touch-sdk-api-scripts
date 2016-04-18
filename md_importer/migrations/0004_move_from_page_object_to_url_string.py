# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('md_importer', '0003_add_herotour_template'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='importedarticle',
            name='page',
        ),
        migrations.AddField(
            model_name='importedarticle',
            name='url',
            field=models.CharField(default='imported', help_text='URL of article, e.g. snappy/guides/security', max_length=300),
            preserve_default=False,
        ),
    ]
