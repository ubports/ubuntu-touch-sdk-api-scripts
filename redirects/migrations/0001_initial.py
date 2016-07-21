# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PathMatchRedirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('match', models.CharField(max_length=256)),
                ('replace', models.CharField(max_length=256)),
                ('preserve_extra', models.BooleanField(default=True)),
                ('precedence', models.IntegerField(help_text=b'Auto-calculated, leave blank', blank=True)),
            ],
        ),
    ]
