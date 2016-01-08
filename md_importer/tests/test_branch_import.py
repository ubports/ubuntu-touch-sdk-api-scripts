from django.test import TestCase

from cms.models import Page

from md_importer.importer.article import Article
from .utils import (
    db_create_home_page,
    db_empty_page_list,
    SnapcraftTestRepo,
)


class TestBranchImport(TestCase):
    def setUp(self):
        db_empty_page_list()
        self.home = db_create_home_page()
        self.assertEqual(len(Page.objects.filter(publisher_is_draft=False)), 0)
        self.assertEqual(len(Page.objects.filter(publisher_is_draft=True)), 1)
        self.assertEqual(Page.objects.all()[0].get_absolute_url(), '/en/')
        self.snapcraft = SnapcraftTestRepo()
        self.repo = self.snapcraft.repo
        self.assertEqual(len(self.repo.directives), 0)


class TestOneDirImport(TestBranchImport):
    def runTest(self):
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertGreater(len(self.repo.imported_articles), 3)
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        self.assertGreater(len(pages), len(self.repo.imported_articles))
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))


class TestOneDirAndTwoFilesImport(TestBranchImport):
    def runTest(self):
        self.repo.add_directive('docs', '')
        self.repo.add_directive('README.md', '')
        self.repo.add_directive('HACKING.md', 'hacking')
        self.assertEqual(len(self.repo.directives), 3)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertGreater(len(self.repo.imported_articles), 5)
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        self.assertEqual(len(pages), len(self.repo.imported_articles))
        self.assertGreater(len(pages), 5)
        self.assertIn(u'/en/', [p.get_absolute_url() for p in pages])
        self.assertIn(u'/en/hacking/', [p.get_absolute_url() for p in pages])


class TestArticletreeOneFileImport(TestBranchImport):
    '''Check if all importe article has 'home' as parent.'''
    def runTest(self):
        self.repo.add_directive('README.md', 'readme')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertEqual(len(self.repo.imported_articles), 1)
        self.assertTrue(self.repo.publish())
        self.assertEqual(Page.objects.count(), 1+1)  # readme + home
        self.assertEqual(self.repo.pages[0].parent, self.home)


class TestArticletreeOneDirImport(TestBranchImport):
    '''Check if all imported articles have 'home' as parent.'''
    def runTest(self):
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        for page in Page.objects.filter(publisher_is_draft=False):
            if page.parent is not None:
                self.assertEqual(page.parent_id, self.home.id)
