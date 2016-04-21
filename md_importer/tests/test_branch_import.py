from datetime import datetime
import os
import pytz
import shutil

from cms.models import Page

from md_importer.importer import (
    DEFAULT_TEMPLATE,
    TEMPLATE_CHOICES,
)
from md_importer.importer.article import Article
from md_importer.importer.publish import find_text_plugin
from md_importer.importer.tools import remove_trailing_slash

from .utils import (
    PublishedPages,
    TestLocalBranchImport,
)


class TestImportDirectivesBuildHierarchyImport(TestLocalBranchImport):
    '''
    Build a article tree structure from files in the snapcraft tree.
    Make sure the top-most articles (in the tree hierarchy) are imported
    first, so the tree looks like this:
    a
    +-- b
        +------ c
        |       +-- d
        |       |   +-- e
        |       |       +-- f
        +-- c2  |
                +-- d2
    Files in the import directives are random in the beginning.
    '''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs/debug.md', 'a/b/c/d')
        self.repo.add_directive('docs/intro.md', 'a/b')
        self.repo.add_directive('docs/mir-snaps.md', 'a/b/c/d/e/f')
        self.repo.add_directive('docs/reference.md', 'a')
        self.repo.add_directive('docs/snapcraft-advanced-features.md', 'a/b/c')
        self.repo.add_directive('docs/snapcraft-syntax.md', 'a/b/c2')
        self.repo.add_directive('docs/upload-your-snap.md', 'a/b/c/d2')
        self.repo.add_directive('docs/get-started.md', 'a/b/c/d/e')
        self.assertEqual(len(self.repo.directives), 8)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertEqual(len(self.repo.imported_articles), 8)
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        self.assertGreater(pages.count(), len(self.repo.imported_articles))
        # Make sure we got the parents right
        for article in self.repo.imported_articles:
            parent_url = remove_trailing_slash(
                article.article_page.page.parent.get_absolute_url())
            url = remove_trailing_slash(
                article.article_page.page.get_absolute_url())
            self.assertEqual(parent_url, os.path.split(url)[0])
            self.assertIsInstance(article, Article)


class TestOneDirImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertGreater(len(self.repo.imported_articles), 10)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            len(self.repo.imported_articles)+1))  # + landing/index page
        for article in self.repo.imported_articles:
            self.assertIsInstance(article, Article)


class TestOneDirAndTwoFilesImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.repo.add_directive('README.md', '')
        self.repo.add_directive('HACKING.md', 'hacking')
        self.assertEqual(len(self.repo.directives), 3)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertGreater(len(self.repo.imported_articles), 10)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            len(self.repo.imported_articles)))
        self.assertTrue(published_pages.has_at_least_size(10))
        self.assertTrue(published_pages.contains_url(u'/en/'))
        self.assertTrue(published_pages.contains_url('/en/hacking/'))


class TestArticletreeOneFileImport(TestLocalBranchImport):
    '''Check if all importe article has 'root' as parent.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('README.md', 'readme')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertEqual(len(self.repo.imported_articles), 1)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            1+1,  # readme + root
        ))
        self.assertEqual(self.repo.pages[0].parent, self.root)


class TestArticletreeOneDirImport(TestLocalBranchImport):
    '''Check if all imported articles have 'root' as parent.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        for page in published_pages.pages:
            if page.parent is not None:
                self.assertEqual(page.parent_id, self.root.id)


class TestArticleHTMLTagsAfterImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertGreater(len(self.repo.imported_articles), 10)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            len(self.repo.imported_articles)+1))  # + landing/index page
        for article in self.repo.imported_articles:
            self.assertIsInstance(article, Article)
            self.assertNotIn('<body>', article.html)
            self.assertNotIn('&lt;body&gt;', article.html)


class TestNoneInURLAfterImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertGreater(len(self.repo.imported_articles), 10)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            len(self.repo.imported_articles)+1))  # + landing/index page
        for article in self.repo.imported_articles:
            self.assertIsInstance(article, Article)
            self.assertNotIn('/None/', article.full_url)
        for page in published_pages.pages:
            self.assertIsNotNone(page.get_slug())


class TestAdvertiseImport(TestLocalBranchImport):
    '''Check if all imported articles are advertised in the navigation when
       using defaults.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        for article in self.repo.imported_articles:
            self.assertTrue(article.advertise)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        for page in published_pages.pages:
            if page.parent is not None:
                parent = page.parent.get_public_object()
                self.assertEqual(parent.id, self.root.id)
                self.assertTrue(page.in_navigation)


class TestNoAdvertiseImport(TestLocalBranchImport):
    '''Check if all imported articles are advertised in the navigation when
       using defaults.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '', advertise=False)
        self.assertTrue(self.repo.execute_import_directives())
        for article in self.repo.imported_articles:
            self.assertFalse(article.advertise)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        for page in published_pages.pages:
            if page.parent is not None:
                self.assertEqual(page.parent_id, self.root.id)
                self.assertFalse(page.in_navigation)


class TestTwiceImport(TestLocalBranchImport):
    '''Run import on the same contents twice, make sure we don't
       add new pages over and over again.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            len(self.repo.imported_articles)+1))  # articles + root
        # Run second import
        shutil.rmtree(self.tempdir)
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertEqual(len(self.repo.imported_articles), 0)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            len(self.repo.imported_articles)+1))  # articles + root


class TestTwiceImportNoHtmlChange(TestLocalBranchImport):
    '''Run import on the same contents twice, make sure we don't
       update the HTML in the pages over and over again.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        self.assertTrue(published_pages.has_size(
            len(self.repo.imported_articles)+1))  # articles + root
        shutil.rmtree(self.tempdir)
        # Take the time before publishing the second import
        now = datetime.now(pytz.utc)
        # Run second import
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertEqual(len(self.repo.imported_articles), 0)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        # Check the page's plugins
        published_pages.update()
        for page in published_pages.pages:
            if page != self.root:
                plugin = find_text_plugin(page)
                self.assertGreater(now, plugin.changed_date)


class TestImportNoTemplateChange(TestLocalBranchImport):
    '''Check if all imported articles use the default template.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        for article in self.repo.imported_articles:
            self.assertEqual(article.template, DEFAULT_TEMPLATE)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        for page in published_pages.pages:
            if page.parent is not None:
                self.assertEqual(page.template, DEFAULT_TEMPLATE)


class TestImportTemplateChange(TestLocalBranchImport):
    '''Check if all imported articles use the desired template.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        template_to_use = TEMPLATE_CHOICES[1][0]
        self.repo.add_directive('docs', '', template=template_to_use)
        self.assertTrue(self.repo.execute_import_directives())
        for article in self.repo.imported_articles:
            self.assertEqual(article.template, template_to_use)
        self.assertTrue(self.repo.publish())
        published_pages = PublishedPages()
        for page in published_pages.pages:
            if page.parent is not None:
                self.assertEqual(page.template, template_to_use)
