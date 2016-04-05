import os

from django.test import TestCase
from cms.api import publish_pages
from cms.models import Page

from md_importer.importer import DEFAULT_LANG
from md_importer.importer.process import process_branch
from md_importer.models import (
    ExternalDocsBranch,
    ExternalDocsBranchImportDirective,
    ImportedArticle,
)
from .utils import (
    db_add_empty_page,
    db_create_root_page,
    db_empty_page_list,
)


class TestImportProcessPasses(TestCase):
    def runTest(self):
        db_empty_page_list()
        root = db_create_root_page()
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


class TestImportProcessBranchWhichChangesFiles(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        ExternalDocsBranch.objects.all().delete()
        ExternalDocsBranchImportDirective.objects.all().delete()
        ImportedArticle.objects.all().delete()
        branch, created = ExternalDocsBranch.objects.get_or_create(
            origin=os.path.join(
                os.path.dirname(__file__), 'data/link-test'),
            branch_name='')
        a, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='', write_to='', external_docs_branch=branch)
        self.assertTrue(process_branch(branch))
        self.assertEqual(
            Page.objects.filter(publisher_is_draft=False).count(), 3)
        branch.origin = os.path.join(
            os.path.dirname(__file__), 'data/link2-test')
        branch.save()
        self.assertTrue(process_branch(branch))
        self.assertEqual(
            Page.objects.filter(publisher_is_draft=False).count(), 3)


class TestImportProcessTwice(TestCase):
    '''
    This is a pretty standard snapcraft import. snappy/build-apps are
    already created. Running the import twice used to create problems,
    because the snappy/build-apps used to be deleted at the end of
    process.process_branch. This test will make sure this will never
    happen again.
    '''
    def runTest(self):
        db_empty_page_list()
        root = db_create_root_page()
        snappy_page = db_add_empty_page('Snappy', root)
        build_apps = db_add_empty_page(
            'Build Apps', snappy_page, slug='build-apps')
        publish_pages([snappy_page, build_apps])
        ExternalDocsBranch.objects.all().delete()
        ExternalDocsBranchImportDirective.objects.all().delete()
        ImportedArticle.objects.all().delete()
        branch, created = ExternalDocsBranch.objects.get_or_create(
            origin=os.path.join(
                os.path.dirname(__file__), 'data/snapcraft-test'),
            branch_name='')
        a, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs/intro.md', write_to='snappy/build-apps',
            external_docs_branch=branch)
        b, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs', write_to='snappy/build-apps',
            external_docs_branch=branch)
        repo = process_branch(branch)
        self.assertIsNotNone(repo)
        self.assertGreater(len(repo.pages), 3)
        self.assertIn(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG),
            [p.get_absolute_url() for p in repo.pages])
        published_pages = Page.objects.filter(publisher_is_draft=False)
        self.assertIn(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG),
            [p.get_absolute_url() for p in published_pages])
        self.assertGreater(published_pages.count(), 3)

        # Run the import a second time
        repo = process_branch(branch)
        self.assertIsNotNone(repo)
        self.assertGreater(len(repo.pages), 3)
        self.assertIn(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG),
            [p.get_absolute_url() for p in repo.pages])
        published_pages = Page.objects.filter(publisher_is_draft=False)
        self.assertIn(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG),
            [p.get_absolute_url() for p in published_pages])
        self.assertGreater(published_pages.count(), 3)
