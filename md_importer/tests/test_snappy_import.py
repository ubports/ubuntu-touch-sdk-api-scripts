from cms.api import publish_pages
from cms.models import Page

from md_importer.importer.repo import Repo
from md_importer.importer.article import Article
from .utils import (
    db_add_empty_page,
    PublishedPages,
    TestLocalBranchImport,
)


class TestSnappyDevelImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snappy-test')
        snappy_page = db_add_empty_page('Snappy', self.root)
        guides = db_add_empty_page('Guides', snappy_page)
        publish_pages([snappy_page, guides])
        self.assertTrue(isinstance(self.repo, Repo))
        self.repo.add_directive('docs', 'snappy/guides/devel')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        for article in self.repo.imported_articles:
            self.assertTrue(isinstance(article, Article))
        self.assertGreater(len(self.repo.pages), 0)
        devel = Page.objects.filter(parent=guides.get_public_object())
        self.assertEqual(devel.count(), 1)
        published_pages = PublishedPages()
        for page in published_pages.pages:
            if page not in [self.root, snappy_page, guides, devel[0]]:
                self.assertEqual(page.parent, devel[0])
