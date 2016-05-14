# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developer_portal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawhtml',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='developer_portal_rawhtml', primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
    ]
