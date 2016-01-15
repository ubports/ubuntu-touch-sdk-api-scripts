import os

from django.test import TestCase
from cms.api import publish_pages

from md_importer.importer.process import process_branch
from md_importer.models import (
    ExternalDocsBranch,
    ExternalDocsBranchImportDirective,
    ImportedArticle,
)
from .utils import (
    db_add_empty_page,
    db_empty_page_list,
)


class TestImportProcessPasses(TestCase):
    def runTest(self):
        db_empty_page_list()
        root = db_add_empty_page('root')
        snappy_page = db_add_empty_page('Snappy', root)
        build_apps = db_add_empty_page('Build Apps', snappy_page)
        publish_pages([snappy_page, build_apps])
        ExternalDocsBranch.objects.all().delete()
        ExternalDocsBranchImportDirective.objects.all().delete()
        ImportedArticle.objects.all().delete()
        branch, created = ExternalDocsBranch.objects.get_or_create(
            origin=os.path.join(
                os.path.dirname(__file__), 'data/snapcraft-test'),
            branch_name='')
        a, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='README.md', write_to='snappy/build-apps/devel',
            external_docs_branch=branch)
        b, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs', write_to='snappy/build-apps/devel',
            external_docs_branch=branch)
        c, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='HACKING.md',
            write_to='snappy/build-apps/devel/hacking',
            external_docs_branch=branch)
        self.assertTrue(process_branch(branch))
