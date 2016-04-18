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
    check_repo,
    check_imported_article,
    db_add_empty_page,
    db_create_root_page,
    db_empty_page_list,
    PublishedPages,
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
        self.assertIsNotNone(process_branch(branch))


class TestPageStateAfterImportProcess(TestCase):
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
        self.assertIsNotNone(process_branch(branch))
        for imported_article in ImportedArticle.objects.all():
            self.assertTrue(check_imported_article(imported_article))


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
        self.assertIsNotNone(process_branch(branch))
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(3))
        branch.origin = os.path.join(
            os.path.dirname(__file__), 'data/link2-test')
        branch.save()
        self.assertTrue(process_branch(branch))
        published_pages.update()
        self.assertTrue(published_pages.has_size(3))


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
        self.assertTrue(check_repo(repo))
        self.assertGreater(len(repo.pages), 10)
        self.assertTrue(repo.contains_page(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        published_pages = PublishedPages()
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.has_at_least_size(10))
        for imported_article in ImportedArticle.objects.all():
            self.assertTrue(check_imported_article(imported_article))

        # Run the import a second time
        repo = process_branch(branch)
        self.assertTrue(check_repo(repo))
        self.assertGreater(len(repo.pages), 10)
        self.assertTrue(repo.contains_page(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        published_pages.update()
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.has_at_least_size(10))
        for imported_article in ImportedArticle.objects.all():
            self.assertTrue(check_imported_article(imported_article))


class TestWholeImportProcessTwiceVariantA(TestCase):
    '''
    This is a pretty standard snapcraft import. snappy/build-apps are
    already created. Running the import twice used to create problems,
    because the snappy/build-apps used to be deleted at the end of
    process.process_branch. This test will make sure this will never
    happen again.
    This time we test a whole import, ie Snappy + Snapcraft twice.
    '''
    def runTest(self):
        db_empty_page_list()
        self.assertEqual(Page.objects.count(), 0)
        root = db_create_root_page()
        snappy_page = db_add_empty_page('Snappy', root)
        build_apps = db_add_empty_page(
            'Build Apps', snappy_page, slug='build-apps')
        guides = db_add_empty_page('Guides', snappy_page)
        phone = db_add_empty_page('Phone', root)
        publish_pages([snappy_page, build_apps, guides, phone])
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(5))
        ExternalDocsBranch.objects.all().delete()
        ExternalDocsBranchImportDirective.objects.all().delete()
        ImportedArticle.objects.all().delete()

        # Snapcraft import definition
        snapcraft_branch, created = ExternalDocsBranch.objects.get_or_create(
            origin=os.path.join(
                os.path.dirname(__file__), 'data/snapcraft-test'),
            branch_name='')
        a, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs/intro.md', write_to='snappy/build-apps',
            external_docs_branch=snapcraft_branch)
        b, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs', write_to='snappy/build-apps',
            external_docs_branch=snapcraft_branch)

        # Snappy import definition
        snappy_branch, created = ExternalDocsBranch.objects.get_or_create(
            origin=os.path.join(
                os.path.dirname(__file__), 'data/snappy-test'),
            branch_name='')
        c, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs', write_to='snappy/guides',
            external_docs_branch=snappy_branch)

        # Run the import a first time
        snapcraft_repo = process_branch(snapcraft_branch)
        self.assertTrue(check_repo(snapcraft_repo))
        self.assertGreater(len(snapcraft_repo.pages), 10)
        self.assertTrue(snapcraft_repo.contains_page(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        snappy_repo = process_branch(snappy_branch)
        self.assertTrue(check_repo(snappy_repo))
        self.assertGreater(len(snappy_repo.pages), 10)
        self.assertTrue(snappy_repo.contains_page(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))

        published_pages = PublishedPages()
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.has_at_least_size(20))
        for imported_article in ImportedArticle.objects.all():
            self.assertTrue(check_imported_article(imported_article))

        # Run the import a second time
        snapcraft_repo = process_branch(snapcraft_branch)
        self.assertTrue(check_repo(snapcraft_repo))
        self.assertGreater(len(snapcraft_repo.pages), 10)
        self.assertTrue(snapcraft_repo.contains_page(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        snappy_repo = process_branch(snappy_branch)
        self.assertTrue(check_repo(snappy_repo))
        self.assertGreater(len(snappy_repo.pages), 10)
        self.assertTrue(snappy_repo.contains_page(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))

        published_pages.update()
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.has_at_least_size(20))
        for imported_article in ImportedArticle.objects.all():
            self.assertTrue(check_imported_article(imported_article))


class TestWholeImportProcessTwiceVariantB(TestCase):
    '''
    This is a pretty standard snapcraft import. snappy/build-apps are
    already created. Running the import twice used to create problems,
    because the snappy/build-apps used to be deleted at the end of
    process.process_branch. This test will make sure this will never
    happen again.
    This time we test a whole import, ie Snappy + Snapcraft twice.
    '''
    def runTest(self):
        db_empty_page_list()
        self.assertEqual(Page.objects.count(), 0)
        root = db_create_root_page()
        snappy_page = db_add_empty_page('Snappy', root)
        guides = db_add_empty_page('Guides', snappy_page)
        publish_pages([snappy_page, guides])
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(3))
        ExternalDocsBranch.objects.all().delete()
        ExternalDocsBranchImportDirective.objects.all().delete()
        ImportedArticle.objects.all().delete()

        # Snapcraft import definition
        snapcraft_branch, created = ExternalDocsBranch.objects.get_or_create(
            origin=os.path.join(
                os.path.dirname(__file__), 'data/snapcraft-test'),
            branch_name='')
        a, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs/intro.md', write_to='snappy/build-apps',
            external_docs_branch=snapcraft_branch)
        b, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs', write_to='snappy/build-apps',
            external_docs_branch=snapcraft_branch)

        # Snappy import definition
        snappy_branch, created = ExternalDocsBranch.objects.get_or_create(
            origin=os.path.join(
                os.path.dirname(__file__), 'data/snappy-test'),
            branch_name='')
        c, created = ExternalDocsBranchImportDirective.objects.get_or_create(
            import_from='docs', write_to='snappy/guides',
            external_docs_branch=snappy_branch)

        # Run the import a first time
        snapcraft_repo = process_branch(snapcraft_branch)
        self.assertTrue(check_repo(snapcraft_repo))
        self.assertGreater(len(snapcraft_repo.pages), 10)
        self.assertTrue(snapcraft_repo.contains_page(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        snappy_repo = process_branch(snappy_branch)
        self.assertTrue(check_repo(snappy_repo))
        self.assertGreater(len(snappy_repo.pages), 10)
        self.assertTrue(snappy_repo.contains_page(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))

        published_pages = PublishedPages()
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.has_at_least_size(20))
        for imported_article in ImportedArticle.objects.all():
            self.assertTrue(check_imported_article(imported_article))

        # Run the import a second time
        snapcraft_repo = process_branch(snapcraft_branch)
        self.assertTrue(check_repo(snapcraft_repo))
        self.assertGreater(len(snapcraft_repo.pages), 10)
        self.assertTrue(snapcraft_repo.contains_page(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        snappy_repo = process_branch(snappy_branch)
        self.assertTrue(check_repo(snappy_repo))
        self.assertGreater(len(snappy_repo.pages), 10)
        self.assertTrue(snappy_repo.contains_page(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))

        published_pages.update()
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/build-apps/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.contains_url(
            '/{}/snappy/guides/'.format(DEFAULT_LANG)))
        self.assertTrue(published_pages.has_at_least_size(20))
        for imported_article in ImportedArticle.objects.all():
            self.assertTrue(check_imported_article(imported_article))
