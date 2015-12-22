from django.test import TestCase

from cms.api import publish_pages
from cms.models import Page

from ..management.importer.repo import SnappyRepo
from ..management.importer.article import SnappyArticle
from .utils import (
    db_add_empty_page,
    db_create_home_page,
    db_empty_page_list,
    SnappyTestRepo,
)


class TestSnappyImport(TestCase):
    def test_snappy_devel_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        snappy_page = db_add_empty_page('Snappy', home)
        guides = db_add_empty_page('Guides', snappy_page)
        publish_pages([home, snappy_page, guides])
        snappy = SnappyTestRepo()
        snappy.repo.reset()
        self.assertEqual(snappy.fetch_retcode, 0)
        self.assertTrue(isinstance(snappy.repo, SnappyRepo))
        snappy.repo.add_directive('docs', '/snappy/guides/devel')
        snappy.repo.execute_import_directives()
        snappy.repo.publish()
        for article in snappy.repo.imported_articles:
            self.assertTrue(isinstance(article, SnappyArticle))
        self.assertGreater(len(snappy.repo.pages), 0)
        devel = Page.objects.filter(parent=guides.get_public_object())
        self.assertEqual(devel.count(), 1)
        for page in Page.objects.filter(publisher_is_draft=False):
            if page not in [home, snappy_page, guides, devel[0]]:
                self.assertEqual(page.parent, devel[0])

    def test_snappy_current_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        snappy_page = db_add_empty_page('Snappy', home)
        guides = db_add_empty_page('Guides', snappy_page)
        publish_pages([home, snappy_page, guides])
        snappy = SnappyTestRepo()
        snappy.repo.reset()
        self.assertTrue(isinstance(snappy.repo, SnappyRepo))
        snappy.repo.add_directive('docs', '/snappy/guides/current')
        snappy.repo.execute_import_directives()
        snappy.repo.publish()
        number_of_articles = len(snappy.repo.imported_articles)
        for article in snappy.repo.imported_articles:
            self.assertTrue(isinstance(article, SnappyArticle))
        self.assertGreater(number_of_articles, 0)
        pages = Page.objects.all()
        current_search = [
            a for a in pages
            if a.get_slug('current') and
            a.get_absolute_url().endswith('snappy/guides/current/')]
        self.assertEqual(len(current_search), 1)
        current = current_search[0]
        nav_pages = [home, snappy_page, guides, current]
        # 1 imported article, 1 redirect
        self.assertEqual(
            number_of_articles*2, pages.count()-len(nav_pages))
        for page in [a for a in pages if a not in nav_pages]:
            if page.get_redirect('en'):
                self.assertEqual(page.parent, guides)
            else:
                self.assertEqual(page.parent, current)
