# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('md_importer', '0002_hero_tour_changes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externaldocsbranchimportdirective',
            name='template',
            field=models.CharField(default=b'default.html', help_text='Django CMS template to use for the imported articles. Default: default.html', max_length=50, choices=[(b'default.html', b'Default'), (b'landing_page.html', b'Landing Page'), (b'no_subnav.html', b'Without Subnav'), (b'with_hero.html', b'With Hero'), (b'snappy_hero_tour.html', b'Snappy Hero Tour')]),
        ),
    ]
