import os

from django.test import TestCase

from md_importer.importer.article import Article

from .utils import (
    db_create_root_page,
    db_empty_page_list,
    PublishedPages,
)


class TestArticleCreate(TestCase):
    def runTest(self):
        fn = os.path.join(
            os.path.dirname(__file__),
            'data/snapcraft-test/docs/plugins.md')
        article = Article(fn, 'plugins')
        self.assertTrue(article.read())


class TestArticlePublish(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        fn = os.path.join(
            os.path.dirname(__file__),
            'data/snapcraft-test/docs/plugins.md')
        article = Article(fn, 'plugins')
        self.assertTrue(article.read())
        self.assertTrue(article.add_to_db())
        self.assertTrue(article.publish())


class TestArticlePublishTwiceNoHTMLChange(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        fn = os.path.join(
            os.path.dirname(__file__),
            'data/snapcraft-test/docs/plugins.md')
        article = Article(fn, 'plugins')
        self.assertTrue(article.read())
        self.assertTrue(article.add_to_db())
        self.assertTrue(article.publish())
        html = article.html
        self.assertGreater(
            len(html), len(open(fn).read()))
        self.assertTrue(article.publish())
        self.assertEqual(html, article.html)
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1+1))  # Root + article page


class TestArticleImportTwiceNoHTMLChange(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        fn = os.path.join(
            os.path.dirname(__file__),
            'data/snapcraft-test/docs/plugins.md')
        article = Article(fn, 'plugins')
        self.assertTrue(article.read())
        self.assertTrue(article.add_to_db())
        self.assertTrue(article.publish())
        html = article.html
        self.assertGreater(
            len(html), len(open(fn).read()))
        article = Article(fn, 'plugins')
        self.assertTrue(article.read())
        self.assertTrue(article.add_to_db())
        self.assertTrue(article.publish())
        self.assertEqual(html, article.html)
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1+1))  # Root + article page
