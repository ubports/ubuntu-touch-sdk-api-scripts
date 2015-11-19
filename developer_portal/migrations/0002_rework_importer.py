# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developer_portal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalDocsBranchImportDirective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('import_from', models.CharField(help_text='File or directory to import from the branch. Ie: "docs/intro.md" (file) or "docs" (complete directory), etc.', max_length=150)),
                ('write_to', models.CharField(help_text='Article URL (for a specific file) or article namespace for a directory or a set of files.', max_length=150)),
            ],
        ),
        migrations.AlterModelOptions(
            name='externaldocsbranch',
            options={'verbose_name': 'external docs branch', 'verbose_name_plural': 'external docs branches'},
        ),
        migrations.RenameField(
            model_name='externaldocsbranch',
            old_name='lp_origin',
            new_name='branch_origin',
        ),
        migrations.RemoveField(
            model_name='externaldocsbranch',
            name='docs_namespace',
        ),
        migrations.RemoveField(
            model_name='externaldocsbranch',
            name='index_doc',
        ),
        migrations.AddField(
            model_name='externaldocsbranch',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='externaldocsbranch',
            name='post_checkout_command',
            field=models.CharField(help_text='Command to run after checkout of the branch.', max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='externaldocsbranchimportdirective',
            name='external_docs_branch',
            field=models.ForeignKey(to='developer_portal.ExternalDocsBranch'),
        ),
    ]
