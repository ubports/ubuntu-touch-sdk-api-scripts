# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirects', '0002_auto_20160720_1339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pathmatchredirect',
            name='match',
            field=models.CharField(help_text=b'Path prefix to match for this redirect. Matches against the start of the requested path. Example: /my/path/', max_length=256),
        ),
        migrations.AlterField(
            model_name='pathmatchredirect',
            name='replace',
            field=models.CharField(help_text=b'Replacement path. Example: /replacement/path/', max_length=256),
        ),
    ]
