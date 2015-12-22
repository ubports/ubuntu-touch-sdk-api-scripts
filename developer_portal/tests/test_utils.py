from django.test import TestCase

from cms.api import publish_pages
from cms.models import Page

from .utils import (
    db_add_empty_page,
    db_create_home_page,
    db_empty_page_list,
)


class PageDBActivities(TestCase):
    def test_empty_page_list(self):
        db_empty_page_list()
        self.assertEqual(Page.objects.count(), 0)

    def test_create_home_page(self):
        db_empty_page_list()
        home = db_create_home_page()
        publish_pages([home])
        self.assertNotEqual(home, None)
        self.assertEqual(Page.objects.count(), 1)

    def test_simple_articletree(self):
        db_empty_page_list()
        home = db_create_home_page()
        snappy = db_add_empty_page('Snappy', home)
        guides = db_add_empty_page('Guides', snappy)
        publish_pages([home, snappy, guides])
        self.assertEqual(Page.objects.count(), 3)
        self.assertEqual(guides.parent, snappy)
        self.assertEqual(snappy.parent, home)
