# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('md_importer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='externaldocsbranchimportdirective',
            name='advertise',
            field=models.BooleanField(default=True, help_text='Should the imported articles be listed in the navigation? Default: yes.'),
        ),
    ]
