from bs4 import BeautifulSoup

from django.http.response import HttpResponseNotFound
from django.test import Client

from cms.models import Page

from md_importer.importer.article import Article
from .utils import TestLocalBranchImport


class TestLinkRewrite(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/link-test')
        self.repo.add_directive('', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        self.assertEqual(pages.count(), 1+2)  # Home + 2 articles
        c = Client()
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                if not link.has_attr('class') or \
                   'headeranchor-link' not in link.attrs['class']:
                    res = c.get(link.attrs['href'])
                    self.assertNotIsInstance(
                        res, HttpResponseNotFound,
                        msg='Link {} not found.'.format(link.attrs['href']))
