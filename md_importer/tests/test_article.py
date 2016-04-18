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


class TestArticleLinkRewrite(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        path = os.path.join(
            os.path.dirname(__file__), 'data/snapcraft-test/docs/')

        # Read first article
        intro_fn = os.path.join(path, 'intro.md')
        intro = Article(intro_fn, 'intro')
        self.assertTrue(intro.read())
        self.assertTrue(intro.add_to_db())
        html = intro.html

        # Read second article
        get_started_fn = os.path.join(path, 'get-started.md')
        get_started = Article(get_started_fn, 'get-started')
        self.assertTrue(get_started.read())
        self.assertTrue(get_started.add_to_db())

        # Replace just one link: [get set up](get-started.md)
        intro.replace_links(
            {get_started_fn: 'get set up'},
            {get_started_fn: get_started})
        self.assertNotEqual(html, intro.html)
        self.assertTrue(intro.publish())


class TestArticleLinkRewriteTwice(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        path = os.path.join(
            os.path.dirname(__file__), 'data/snapcraft-test/docs/')

        # Read first article
        intro_fn = os.path.join(path, 'intro.md')
        intro = Article(intro_fn, 'intro')
        self.assertTrue(intro.read())
        self.assertTrue(intro.add_to_db())
        html = intro.html

        # Read second article
        get_started_fn = os.path.join(path, 'get-started.md')
        get_started = Article(get_started_fn, 'get-started')
        self.assertTrue(get_started.read())
        self.assertTrue(get_started.add_to_db())

        # Replace just one link: [get set up](get-started.md)
        intro.replace_links(
            {get_started_fn: 'get set up'},
            {get_started_fn: get_started})
        # Check if the HTML changed because of replaced links
        self.assertNotEqual(html, intro.html)
        self.assertTrue(intro.publish())

        # Now check if the HTML will change after a second run
        html = intro.html

        # 2nd time: Read first article
        intro = Article(intro_fn, 'intro')
        self.assertTrue(intro.read())
        self.assertTrue(intro.add_to_db())

        # 2nd time: Read second article
        get_started = Article(get_started_fn, 'get-started')
        self.assertTrue(get_started.read())
        self.assertTrue(get_started.add_to_db())

        # 2nd time: Replace just one link: [get set up](get-started.md)
        intro.replace_links(
            {get_started_fn: 'get set up'},
            {get_started_fn: get_started})
        self.assertTrue(intro.publish())

        # After the second run, the HTML should still be the same
        self.assertEqual(html, intro.html)
