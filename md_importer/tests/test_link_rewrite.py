from bs4 import BeautifulSoup

from cms.api import publish_pages
from cms.models import Page

from md_importer.importer.article import Article
from .utils import (
    db_add_empty_page,
    TestLocalBranchImport,
)


class TestLinkRewrite(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/link-test')
        self.repo.add_directive('', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        self.assertEqual(pages.count(), 1+2)  # Home + 2 articles
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            self.assertEqual(article.page.parent, self.home)
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                if not link.has_attr('class') or \
                   'headeranchor-link' not in link.attrs['class']:
                    self.check_local_link(link.attrs['href'], pages)


class TestSnapcraftLinkRewrite(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        snappy_page = db_add_empty_page('Snappy', self.home)
        build_apps = db_add_empty_page('Build Apps', snappy_page)
        publish_pages([snappy_page, build_apps])
        self.assertEqual(
            3, Page.objects.filter(publisher_is_draft=True).count())
        self.repo.add_directive('docs', 'snappy/build-apps/devel')
        self.repo.add_directive('README.md', 'snappy/build-apps/devel')
        self.repo.add_directive(
            'HACKING.md', 'snappy/build-apps/devel/hacking')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            self.assertGreater(len(article.html), 0)
        for article in self.repo.imported_articles:
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                if not link.has_attr('class') or \
                   'headeranchor-link' not in link.attrs['class']:
                    self.check_local_link(link.attrs['href'], pages)
