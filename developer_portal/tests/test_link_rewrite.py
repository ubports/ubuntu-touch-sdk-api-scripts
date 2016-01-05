import os
import shutil
import tempfile

from django.test import TestCase

from cms.models import Page

from ..management.importer.article import Article
from ..management.importer.repo import create_repo
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
        for article in repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
            print(article.html)
        shutil.rmtree(tempdir)
