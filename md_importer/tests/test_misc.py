from bs4 import BeautifulSoup

from cms.models import Page

from .utils import (
    TestLocalBranchImport,
)


class TestLocalImage(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/local-image-test')
        self.repo.add_directive('', '')
        self.assertFalse(self.repo.execute_import_directives())


class TestRemoteImage(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/remote-image-test')
        self.repo.add_directive('', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        pages = Page.objects.filter(publisher_is_draft=False)
        self.assertEqual(pages.count(), 1+1)  # root + 1 article
        for article in self.repo.imported_articles:
            self.assertEqual(article.page.parent, self.root)
            soup = BeautifulSoup(article.html, 'html5lib')
            for link in soup.find_all('a'):
                page = self.check_local_link(link.attrs['href'])
                self.assertIsNotNone(
                    page,
                    msg='Link {} not found. Available pages: {}'.format(
                        link.attrs['href'],
                        ', '.join([p.get_absolute_url() for p in pages])))
                self.assertIn(page, pages)
