from cms.api import publish_pages
from cms.models import Page

from md_importer.importer import DEFAULT_LANG
from md_importer.importer.repo import SnappyRepo
from md_importer.importer.article import SnappyArticle
from .utils import (
    db_add_empty_page,
    TestLocalBranchImport,
)


class TestSnappyDevelImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snappy-test')
        snappy_page = db_add_empty_page('Snappy', self.root)
        guides = db_add_empty_page('Guides', snappy_page)
        publish_pages([snappy_page, guides])
        self.assertTrue(isinstance(self.repo, SnappyRepo))
        self.repo.add_directive('docs', 'snappy/guides/devel')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, SnappyArticle))
        self.assertGreater(len(self.repo.pages), 0)
        devel = Page.objects.filter(parent=guides.get_public_object())
        self.assertEqual(devel.count(), 1)
        for page in Page.objects.filter(publisher_is_draft=False):
            if page not in [self.root, snappy_page, guides, devel[0]]:
                self.assertEqual(page.parent, devel[0])


class TestSnappyCurrentImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snappy-test')
        snappy_page = db_add_empty_page('Snappy', self.root)
        guides = db_add_empty_page('Guides', snappy_page)
        publish_pages([snappy_page, guides])
        self.assertTrue(isinstance(self.repo, SnappyRepo))
        self.repo.add_directive('docs', 'snappy/guides/current')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        number_of_articles = len(self.repo.imported_articles)
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, SnappyArticle))
        self.assertGreater(number_of_articles, 0)
        pages = Page.objects.filter(publisher_is_draft=False)
        current_search = [
            a for a in pages
            if a.get_slug('current') and
            a.get_absolute_url().endswith('snappy/guides/current/')]
        self.assertEqual(len(current_search), 1)
        current = current_search[0]
        nav_pages = [self.root, snappy_page, guides, current]
        self.assertEqual(
            2*number_of_articles, # Articles + current redirects
            pages.count()-len(nav_pages))
        for page in [a for a in pages if a not in nav_pages]:
            if page.get_redirect(DEFAULT_LANG):
                self.assertEqual(page.parent, guides)
            else:
                self.assertEqual(page.parent, current)
