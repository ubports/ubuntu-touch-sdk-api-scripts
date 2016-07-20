# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pathmatchredirect',
            name='match',
            field=models.CharField(help_text=b'Path prefix to match for this redirect', max_length=256),
        ),
        migrations.AlterField(
            model_name='pathmatchredirect',
            name='preserve_extra',
            field=models.BooleanField(default=True, help_text=b'Should any part of the path after what was matched be appended to the replacement path?'),
        ),
        migrations.AlterField(
            model_name='pathmatchredirect',
            name='replace',
            field=models.CharField(help_text=b'Replacement path', max_length=256),
        ),
    ]
