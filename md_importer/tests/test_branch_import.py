from datetime import datetime
import pytz
import shutil

from cms.models import CMSPlugin, Page

from md_importer.importer.article import Article
from .utils import TestLocalBranchImport


class TestOneDirImport(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertGreater(len(self.repo.imported_articles), 3)
        self.assertTrue(self.repo.publish())
        pages = Page.objects.all()
        self.assertGreater(pages.count(), len(self.repo.imported_articles))
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
        self.assertGreater(len(self.repo.imported_articles), 5)
        self.assertTrue(self.repo.publish())
        pages = Page.objects.filter(publisher_is_draft=False)
        self.assertEqual(pages.count(), len(self.repo.imported_articles))
        self.assertGreater(pages.count(), 5)
        self.assertIn(u'/en/', [p.get_absolute_url() for p in pages])
        self.assertIn(u'/en/hacking/', [p.get_absolute_url() for p in pages])


class TestArticletreeOneFileImport(TestLocalBranchImport):
    '''Check if all importe article has 'root' as parent.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('README.md', 'readme')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertEqual(len(self.repo.imported_articles), 1)
        self.assertTrue(self.repo.publish())
        self.assertEqual(
            1+1,  # readme + root
            Page.objects.filter(publisher_is_draft=False).count())
        self.assertEqual(self.repo.pages[0].parent, self.root)


class TestArticletreeOneDirImport(TestLocalBranchImport):
    '''Check if all imported articles have 'root' as parent.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        for page in Page.objects.filter(publisher_is_draft=False):
            if page.parent is not None:
                self.assertEqual(page.parent_id, self.root.id)


class TestAdvertiseImport(TestLocalBranchImport):
    '''Check if all imported articles are advertised in the navigation when
       using defaults.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        for page in Page.objects.filter(publisher_is_draft=False):
            if page.parent is not None:
                self.assertEqual(page.parent_id, self.root.id)
                self.assertTrue(page.in_navigation)


class TestNoAdvertiseImport(TestLocalBranchImport):
    '''Check if all imported articles are advertised in the navigation when
       using defaults.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '', advertise=False)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        for page in Page.objects.filter(publisher_is_draft=False):
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
        self.assertEqual(
            Page.objects.filter(publisher_is_draft=False).count(),
            len(self.repo.imported_articles)+1)  # articles + root
        # Run second import
        shutil.rmtree(self.tempdir)
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertEqual(len(self.repo.imported_articles), 0)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        self.assertEqual(
            Page.objects.filter(publisher_is_draft=False).count(),
            len(self.repo.imported_articles)+1)  # articles + root


class TestTwiceImportNoHtmlChange(TestLocalBranchImport):
    '''Run import on the same contents twice, make sure we don't
       update the HTML in the pages over and over again.'''
    def runTest(self):
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        self.assertEqual(
            Page.objects.filter(publisher_is_draft=False).count(),
            len(self.repo.imported_articles)+1)  # articles + root
        # Take the time before publishing the second import
        now = datetime.now(pytz.utc)
        shutil.rmtree(self.tempdir)
        # Run second import
        self.create_repo('data/snapcraft-test')
        self.repo.add_directive('docs', '')
        self.assertEqual(len(self.repo.directives), 1)
        self.assertEqual(len(self.repo.imported_articles), 0)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        # Check the page's plugins
        for plugin_change in CMSPlugin.objects.filter(
            plugin_type='RawHtmlPlugin').order_by(
                '-changed_date'):
            self.assertGreater(now, plugin_change.changed_date)
