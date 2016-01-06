from bs4 import BeautifulSoup
import os
import shutil
import tempfile

from django.http.response import HttpResponseNotFound
from django.test import TestCase, Client

from cms.models import Page

from md_importer.importer.article import Article
from md_importer.importer.repo import create_repo
from .utils import (
    db_create_home_page,
    db_empty_page_list,
)


class TestLinkRewrite(TestCase):
    def test_simple_case(self):
        db_empty_page_list()
        db_create_home_page()
        tempdir = tempfile.mkdtemp()
        repo = create_repo(
            tempdir,
            os.path.join(os.path.dirname(__file__), 'data/link-test'),
            '',
            '')
        self.assertEqual(repo.get(), 0)
        repo.add_directive('', '/')
        repo.execute_import_directives()
        repo.publish()
        pages = Page.objects.all()
        self.assertEqual(pages.count(), 1+2)  # Home + 2 articles
        c = Client()
        for article in repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                if not link.has_attr('class') or \
                   'headeranchor-link' not in link.attrs['class']:
                    res = c.get(link.attrs['href'])
                    self.assertNotIsInstance(
                        res, HttpResponseNotFound,
                        msg='Link {} not found.'.format(link.attrs['href']))
        shutil.rmtree(tempdir)
