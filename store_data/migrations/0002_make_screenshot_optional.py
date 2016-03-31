# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gadgetsnap',
            name='screenshot_url',
            field=models.ManyToManyField(to='store_data.ScreenshotURL', blank=True),
        ),
    ]
