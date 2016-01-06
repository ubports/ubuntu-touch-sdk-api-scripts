from django.test import TestCase

from cms.api import publish_pages
from cms.models import Page

from md_importer.importer.article import Article
from .utils import (
    db_create_home_page,
    db_empty_page_list,
    SnapcraftTestRepo,
)


class TestBranchImport(TestCase):
    def test_1dir_import(self):
        db_empty_page_list()
        db_create_home_page()
        snapcraft = SnapcraftTestRepo()
        snapcraft.repo.reset()
        snapcraft.repo.add_directive('docs', '/')
        snapcraft.repo.execute_import_directives()
        snapcraft.repo.publish()
        pages = Page.objects.all()
        self.assertGreater(len(pages), 3)
        for article in snapcraft.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))

    def test_1dir_and_2files_import(self):
        db_empty_page_list()
        db_create_home_page()
        snapcraft = SnapcraftTestRepo()
        snapcraft.repo.reset()
        snapcraft.repo.add_directive('docs', '/')
        snapcraft.repo.add_directive('README.md', '/')
        snapcraft.repo.add_directive('HACKING.md', '/hacking')
        snapcraft.repo.execute_import_directives()
        snapcraft.repo.publish()
        pages = Page.objects.all()
        self.assertGreater(len(pages), 5)
        self.assertIn(u'/en/', [p.get_absolute_url() for p in pages])
        self.assertIn(u'/en/hacking/', [p.get_absolute_url() for p in pages])

    # Check if all importe article has 'home' as parent
    def test_articletree_1file_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        publish_pages([[home]])
        snapcraft = SnapcraftTestRepo()
        snapcraft.repo.reset()
        snapcraft.repo.add_directive('README.md', '/readme')
        snapcraft.repo.execute_import_directives()
        snapcraft.repo.publish()
        self.assertEqual(Page.objects.count(), 1+1)  # readme + home
        self.assertTrue(snapcraft.repo.pages[0].parent == home)

    # Check if all imported articles have 'home' as parent
    def test_articletree_1dir_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        snapcraft = SnapcraftTestRepo()
        snapcraft.repo.reset()
        snapcraft.repo.add_directive('docs', '/')
        snapcraft.repo.execute_import_directives()
        snapcraft.repo.publish()
        for page in Page.objects.filter(publisher_is_draft=False):
            if page.parent is not None:
                self.assertEqual(page.parent_id, home.id)
