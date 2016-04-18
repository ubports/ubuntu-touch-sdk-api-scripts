from bs4 import BeautifulSoup

from cms.models import Page

from ..importer import DEFAULT_LANG
from ..importer.article import Article
from .utils import (
    db_add_empty_page,
    is_local_link,
    PublishedPages,
    TestLocalBranchImport,
)


class TestLinkRewrite(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/link-test')
        self.repo.add_directive('', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1+2))  # root + 2 articles
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            self.assertEqual(article.article_page.page.parent, self.root)
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                page = self.check_local_link(link.attrs['href'])
                self.assertIsNotNone(
                    page,
                    msg='Link {} not found. Available pages: {}'.format(
                        link.attrs['href'],
                        ', '.join(published_pages.urls)))
                self.assertIn(page, published_pages.pages)
            if article.slug == 'file1':
                for link in soup.find_all('a'):
                    if not link.has_attr('class') or \
                       'headeranchor-link' not in link.attrs['class']:
                        self.assertIn(
                            link.attrs['href'],
                            ['/file2', '/{}/file2/'.format(DEFAULT_LANG)])


class TestLinkBrokenRewrite(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/link-broken-test')
        self.repo.add_directive('', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1+2))  # root + 2 articles
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            self.assertEqual(article.article_page.page.parent, self.root)
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                if not link.has_attr('class') or \
                   'headeranchor-link' not in link.attrs['class']:
                    page = self.check_local_link(link.attrs['href'])
                    self.assertIsNone(page)
                    self.assertNotIn(page, published_pages.pages)


class TestNoneNotInLinks(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        snappy_page = db_add_empty_page('Snappy', self.root)
        self.assertFalse(snappy_page.publisher_is_draft)
        build_apps = db_add_empty_page('Build Apps', snappy_page)
        self.assertFalse(build_apps.publisher_is_draft)
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(3))
        self.repo.add_directive('docs/intro.md', 'snappy/build-apps/current')
        self.repo.add_directive('docs', 'snappy/build-apps/current')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            self.assertGreater(len(article.html), 0)
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                if is_local_link(link):
                    self.assertFalse(link.attrs['href'].startswith('/None/'))


class TestSnapcraftLinkRewrite(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        snappy_page = db_add_empty_page('Snappy', self.root)
        self.assertFalse(snappy_page.publisher_is_draft)
        build_apps = db_add_empty_page('Build Apps', snappy_page)
        self.assertFalse(build_apps.publisher_is_draft)
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(3))
        self.repo.add_directive('docs/intro.md', 'snappy/build-apps/current')
        self.repo.add_directive('docs', 'snappy/build-apps/current')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            self.assertGreater(len(article.html), 0)
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                if is_local_link(link):
                    page = self.check_local_link(link.attrs['href'])
                    self.assertIsNotNone(
                        page,
                        msg='Link {} not found. Available pages: {}'.format(
                            link.attrs['href'],
                            ', '.join([p.get_absolute_url() for p in pages])))
                    self.assertIn(page, pages)
