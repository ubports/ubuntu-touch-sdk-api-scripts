from django.core.management.base import BaseCommand

from md_importer.importer import logger
from md_importer.importer.process import process_branch
from md_importer.models import ExternalDocsBranch


def import_branches(selection):
    if not ExternalDocsBranch.objects.count():
        logger.error('No branches registered in the '
                     'ExternalDocsBranch table yet.')
        return
    for branch in ExternalDocsBranch.objects.filter(
            origin__regex=selection, active=True):
        if process_branch(branch) is None:
            break


class Command(BaseCommand):
    help = "Import external branches for documentation."

    def add_arguments(self, parser):
        parser.add_argument('branches', nargs='*')

    def handle(*args, **options):
        branches = options['branches']
        if not branches:
            import_branches('.*')
        else:
            for b in branches:
                import_branches(b)
