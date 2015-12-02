from django.core.management.base import BaseCommand
from django.core.management import call_command

from ..importer.local_branch import LocalBranch, SnappyLocalBranch

import logging
import shutil
import tempfile

from developer_portal.models import (
    ExternalDocsBranch,
    ExternalDocsBranchImportDirective,
)


def import_branches(selection):
    if not ExternalDocsBranch.objects.count():
        logging.error('No branches registered in the '
                      'ExternalDocsBranch table yet.')
        return
    tempdir = tempfile.mkdtemp()
    for branch in ExternalDocsBranch.objects.filter(
            branch_origin__regex=selection, active=True):
        url = branch.branch_origin
        if url.startswith('lp:snappy') or \
           'snappy' in url.split(':')[1].split('.git')[0].split('/'):
            branch_class = SnappyLocalBranch
        else:
            branch_class = LocalBranch
        local_branch = branch_class(tempdir, branch.branch_origin,
                                    branch.post_checkout_command)
        if local_branch.get() != 0:
            break
        for directive in ExternalDocsBranchImportDirective.objects.filter(
                external_docs_branch=branch):
            local_branch.add_directive(directive.import_from,
                                       directive.write_to)
        local_branch.execute_import_directives()
        local_branch.publish()
        local_branch.remove_old_pages()
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
