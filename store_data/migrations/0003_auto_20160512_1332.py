# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_data', '0002_make_screenshot_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gadgetsnap',
            name='icon_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
