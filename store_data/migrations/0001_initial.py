# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Architecture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='GadgetSnap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('icon_url', models.URLField(blank=True)),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=250, null=True, blank=True)),
                ('ratings_average', models.DecimalField(max_digits=2, decimal_places=1)),
                ('alias', models.CharField(max_length=100, null=True, blank=True)),
                ('price', models.DecimalField(max_digits=5, decimal_places=2)),
                ('publisher', models.CharField(max_length=100)),
                ('store_url', models.URLField(blank=True)),
                ('version', models.CharField(max_length=25)),
                ('last_updated', models.DateTimeField()),
                ('description', models.TextField(max_length=5000)),
                ('website', models.URLField(blank=True)),
                ('architecture', models.ManyToManyField(to='store_data.Architecture')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='ScreenshotURL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='gadgetsnap',
            name='release',
            field=models.ManyToManyField(to='store_data.Release'),
        ),
        migrations.AddField(
            model_name='gadgetsnap',
            name='screenshot_url',
            field=models.ManyToManyField(to='store_data.ScreenshotURL'),
        ),
    ]
