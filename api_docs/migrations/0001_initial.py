# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(default=b'', max_length=256, blank=True)),
                ('fullname', models.CharField(max_length=128)),
                ('keywords', models.CharField(default=b'', max_length=256, blank=True)),
                ('data', models.TextField(default=b'', blank=True)),
                ('source_file', models.CharField(max_length=128, null=True, blank=True)),
                ('source_format', models.CharField(max_length=32, null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Rendered Element',
                'verbose_name_plural': 'Rendered Elements',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Namespace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('display_name', models.CharField(default=b'', max_length=64, blank=True)),
                ('data', models.TextField(default=b'', blank=True)),
                ('source_file', models.CharField(max_length=128, null=True, blank=True)),
                ('source_format', models.CharField(max_length=32, null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(max_length=64)),
                ('title', models.CharField(max_length=64)),
                ('description', models.CharField(default=b'', max_length=256, blank=True)),
                ('fullname', models.CharField(max_length=128)),
                ('keywords', models.CharField(default=b'', max_length=256, blank=True)),
                ('data', models.TextField(default=b'', blank=True)),
                ('source_file', models.CharField(max_length=128, null=True, blank=True)),
                ('source_format', models.CharField(max_length=32, null=True, blank=True)),
                ('order_index', models.PositiveIntegerField(default=0, blank=True)),
                ('namespace', models.ForeignKey(blank=True, to='api_docs.Namespace', null=True)),
            ],
            options={
                'ordering': ('order_index',),
                'verbose_name': 'Rendered Page',
                'verbose_name_plural': 'Rendered Pages',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.CharField(max_length=64)),
                ('language', models.ForeignKey(to='api_docs.Language', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='section',
            name='topic_version',
            field=models.ForeignKey(to='api_docs.Version'),
        ),
        migrations.AddField(
            model_name='page',
            name='section',
            field=models.ForeignKey(to='api_docs.Section'),
        ),
        migrations.AddField(
            model_name='namespace',
            name='platform_section',
            field=models.ForeignKey(to='api_docs.Section'),
        ),
        migrations.AddField(
            model_name='language',
            name='current_version',
            field=models.ForeignKey(related_name='current_for_lang', blank=True, to='api_docs.Version', null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='development_version',
            field=models.ForeignKey(related_name='development_for_lang', blank=True, to='api_docs.Version', null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='topic',
            field=models.ForeignKey(to='api_docs.Topic'),
        ),
        migrations.AddField(
            model_name='element',
            name='namespace',
            field=models.ForeignKey(blank=True, to='api_docs.Namespace', null=True),
        ),
        migrations.AddField(
            model_name='element',
            name='section',
            field=models.ForeignKey(to='api_docs.Section'),
        ),
    ]
