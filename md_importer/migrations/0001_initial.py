# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalDocsBranch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('origin', models.CharField(help_text='External branch location, ie: lp:snappy/15.04 or https://github.com/ubuntu-core/snappy.git', max_length=200)),
                ('branch_name', models.CharField(help_text='For use with git branches, ie: "master" or "15.04" or "1.x".', max_length=200, blank=True)),
                ('post_checkout_command', models.CharField(help_text='Command to run after checkout of the branch.', max_length=100, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'external docs branch',
                'verbose_name_plural': 'external docs branches',
            },
        ),
        migrations.CreateModel(
            name='ExternalDocsBranchImportDirective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('import_from', models.CharField(help_text='File or directory to import from the branch. Ie: "docs/intro.md" (file) or "docs" (complete directory), etc.', max_length=150, blank=True)),
                ('write_to', models.CharField(help_text='Article URL (for a specific file) or article namespace for a directory or a set of files.', max_length=150, blank=True)),
                ('external_docs_branch', models.ForeignKey(to='md_importer.ExternalDocsBranch')),
            ],
        ),
        migrations.CreateModel(
            name='ImportedArticle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_import', models.DateTimeField(help_text='Datetime of last import.', verbose_name='Datetime')),
                ('branch', models.ForeignKey(to='md_importer.ExternalDocsBranch')),
                ('page', models.ForeignKey(to='cms.Page')),
            ],
        ),
    ]
