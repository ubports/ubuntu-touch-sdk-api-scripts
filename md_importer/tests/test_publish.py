from django.test import TestCase

from cms.api import add_plugin, publish_pages

from developer_portal.models import RawHtml

from md_importer.importer import DEFAULT_LANG
from md_importer.importer.publish import ArticlePage

from .utils import (
    db_empty_page_list,
    db_create_root_page,
    db_add_empty_page,
    PublishedPages,
)


class TestCreateArticlePage(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1))
        article_page = ArticlePage('Test page', 'test')
        self.assertIsNotNone(article_page)
        article_page.publish()
        published_pages.update()
        self.assertTrue(published_pages.has_size(2))


class TestNewArticlePageForCorrectPlaceholderAndPlugins(TestCase):
    def runTest(self):
        db_empty_page_list()
        db_create_root_page()
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1))
        article_page = ArticlePage('Test page', 'test')
        self.assertIsNotNone(article_page)
        article_page.publish()
        published_pages.update()
        self.assertTrue(published_pages.has_size(2))
        placeholders = article_page.page.placeholders
        self.assertEqual(placeholders.count(), 1)
        plugins = placeholders.all()[0].get_plugins()
        self.assertEqual(plugins.count(), 1)
        self.assertIsInstance(plugins[0].get_plugin_instance()[0], RawHtml)


class TestOldArticlePageForCorrectPlaceholderAndPlugins(TestCase):
    def runTest(self):
        db_empty_page_list()
        root = db_create_root_page()
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1))
        page = db_add_empty_page('Test', parent=root)
        publish_pages(page)
        self.assertIsNotNone(page)
        published_pages.update()
        self.assertTrue(published_pages.has_size(2))
        self.assertEqual(page.placeholders.count(), 1)
        placeholder = page.placeholders.all()[0]
        add_plugin(placeholder, 'TextPlugin', DEFAULT_LANG, body='')
        add_plugin(placeholder, 'TextPlugin', DEFAULT_LANG, body='')
        add_plugin(placeholder, 'TextPlugin', DEFAULT_LANG, body='')
        plugins = placeholder.get_plugins()
        self.assertEqual(plugins.count(), 3)

        article_page = ArticlePage('Test', 'test')
        self.assertIsNotNone(article_page)
        article_page.publish()
        published_pages.update()
        self.assertTrue(published_pages.has_size(2))
        self.assertEqual(article_page.page.placeholders.count(), 1)
        placeholder = article_page.page.placeholders.all()[0]
        plugins = placeholder.get_plugins()
        self.assertEqual(plugins.count(), 1)
        self.assertIsInstance(plugins[0].get_plugin_instance()[0], RawHtml)
