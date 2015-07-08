from django.core.management.base import NoArgsCommand

import logging
import os
import shutil
import subprocess
import tempfile

from developer_portal.models import SnappyDocsBranch


def import_branch(origin, alias):
    return subprocess.call([
        'bzr', 'checkout', '--lightweight', origin, alias])


def clean_up(directory):
    shutil.rmtree(directory)


def import_branches():
    if not SnappyDocsBranch.objects.count():
        logging.error('No Snappy branches registered in the '
                      'SnappyDocsBranch table yet.')
        return
    tempdir = tempfile.mkdtemp()
    pwd = os.getcwd()
    os.chdir(tempdir)
    for branch in SnappyDocsBranch.objects.all():
        if import_branch(branch.branch_origin, branch.path_alias) != 0:
            logging.error(
                'Could not check out branch "%s".' % branch.branch_origin)
            shutil.rmtree(os.path.join(tempdir, branch.path_alias))
            break
    os.chdir(pwd)
    # for local_branch in tempdir:
    # import markdown from local_branch
    shutil.rmtree(tempdir)


class Command(NoArgsCommand):
    help = "Import Snappy branches for documentation."

    def handle_noargs(self, **options):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%F %T')
        import_branches()
