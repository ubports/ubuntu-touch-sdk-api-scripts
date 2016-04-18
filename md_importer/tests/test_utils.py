from django.test import TestCase

from cms.models import Page
from cms.utils.page_resolver import get_page_from_request

from ..importer import DEFAULT_LANG
from .utils import (
    db_add_empty_page,
    db_create_root_page,
    db_empty_page_list,
    PublishedPages,
    TestLocalBranchImport,
)


class PageDBActivities(TestCase):
    def test_empty_page_list(self):
        db_empty_page_list()
        self.assertEqual(Page.objects.count(), 0)

    def test_create_root_page(self):
        db_empty_page_list()
        root = db_create_root_page()
        self.assertNotEqual(root, None)
        self.assertFalse(root.publisher_is_draft)
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(1))

    def test_simple_articletree(self):
        db_empty_page_list()
        root = db_create_root_page()
        self.assertFalse(root.publisher_is_draft)
        snappy = db_add_empty_page('Snappy', root)
        self.assertFalse(snappy.publisher_is_draft)
        guides = db_add_empty_page('Guides', snappy)
        self.assertFalse(guides.publisher_is_draft)
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(3))
        self.assertEqual(guides.parent.get_public_object(), snappy)
        self.assertEqual(snappy.parent.get_public_object(), root)


class TestSimpleURLs(TestLocalBranchImport):
    def runTest(self):
        page = db_add_empty_page('page', self.root)
        self.assertFalse(page.publisher_is_draft)
        request = self.get_request('/en/page', language=DEFAULT_LANG)
        found_page = get_page_from_request(request)
        self.assertIsNotNone(found_page)
        self.assertFalse(found_page.publisher_is_draft)
        self.assertEqual(found_page, page)
