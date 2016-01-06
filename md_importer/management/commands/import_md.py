from django.core.management.base import BaseCommand
from django.core.management import call_command

from md_importer.importer.repo import create_repo

import datetime
import logging
import shutil
import tempfile

from md_importer.models import (
    ExternalDocsBranch,
    ExternalDocsBranchImportDirective,
    ImportedArticle,
)


def import_branches(selection):
    if not ExternalDocsBranch.objects.count():
        logging.error('No branches registered in the '
                      'ExternalDocsBranch table yet.')
        return
    for branch in ExternalDocsBranch.objects.filter(
            origin__regex=selection, active=True):
        tempdir = tempfile.mkdtemp()
        repo = create_repo(tempdir, branch.origin, branch.branch_name,
                           branch.post_checkout_command)
        if repo.get() != 0:
            break
        for directive in ExternalDocsBranchImportDirective.objects.filter(
                external_docs_branch=branch):
            repo.add_directive(directive.import_from,
                               directive.write_to)
        repo.execute_import_directives()
        repo.publish()
        for page in repo.pages:
            ImportedArticle.objects.get_or_create(
                branch=branch,
                page=page,
                last_import=datetime.datetime.now())

        # The import is done, now let's clean up.
        for old_article in ImportedArticle.objects.filter(branch=branch):
            if old_article.page not in repo.pages and \
               old_article.page.changed_by in ['python-api', 'script']:
                old_article.page.delete()
        shutil.rmtree(tempdir)

    # https://stackoverflow.com/questions/33284171/
    call_command('cms', 'fix-tree')


class Command(BaseCommand):
    help = "Import external branches for documentation."

    def add_arguments(self, parser):
        parser.add_argument('branches', nargs='*')

    def handle(*args, **options):
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%F %T')
        branches = options['branches']
        if not branches:
            import_branches('.*')
        else:
            for b in branches:
                import_branches(b)
