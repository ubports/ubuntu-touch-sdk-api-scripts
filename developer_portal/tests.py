import os
import shutil
import tempfile

from django.test import TestCase
from cms.api import create_page
from cms.models import Page

from management.importer.repo import Repo


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


# We are going to re-use this one, so we don't have to checkout the git
# repo all the time.
class GitTestRepo():
    __metaclass__ = Singleton

    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.repo = Repo(
            self.tempdir,
            'https://github.com/ubuntu-core/snapcraft.git',
            'master',
            '')
        self.fetch_retcode = self.repo.get()


def tearDownModule():
    shutil.rmtree(GitTestRepo().tempdir)


def db_empty_page_list():
    Page.objects.all().delete()


def db_create_home_page():
    home = create_page('Test import', 'default.html', 'en', slug='home')
    home.publish('en')
    return home


class PageDBActivities(TestCase):
    def test_empty_page_list(self):
        db_empty_page_list()
        self.assertEqual(Page.objects.count(), 0)

    def test_create_home_page(self):
        db_empty_page_list()
        home = db_create_home_page()
        self.assertNotEqual(home, None)
        self.assertEqual(Page.objects.count(), 2)  # one page, one draft


class TestBranchFetch(TestCase):
    def test_git_fetch(self):
        git_repo = GitTestRepo()
        git_repo.repo.reset()
        self.assertEqual(git_repo.fetch_retcode, 0)

    def test_bzr_fetch(self):
        tempdir = tempfile.mkdtemp()
        l = Repo(
            tempdir,
            'lp:snapcraft',  # outdated, but should work for testing
            '',
            '')
        ret = l.get()
        shutil.rmtree(tempdir)
        self.assertEqual(ret, 0)

    def test_post_checkout_command(self):
        tempdir = tempfile.mkdtemp()
        l = Repo(
            tempdir,
            'lp:snapcraft',
            '',
            'touch something.html'
        )
        ret = l.get()
        self.assertEqual(ret, 0)
        self.assertTrue(os.path.exists(
            os.path.join(l.checkout_location, 'something.html')))
        shutil.rmtree(tempdir)

class TestBranchImport(TestCase):
    def test_1dir_import(self):
        db_empty_page_list()
        db_create_home_page()
        git_repo = GitTestRepo()
        git_repo.repo.reset()
        git_repo.repo.add_directive('docs', '/')
        git_repo.repo.execute_import_directives()
        git_repo.repo.publish()
        pages = Page.objects.all()
        self.assertGreater(len(pages), 3)

    def test_1dir_and_2files_import(self):
        db_empty_page_list()
        db_create_home_page()
        git_repo = GitTestRepo()
        git_repo.repo.reset()
        git_repo.repo.add_directive('docs', '/')
        git_repo.repo.add_directive('README.md', '/')
        git_repo.repo.add_directive('HACKING.md', '/hacking')
        git_repo.repo.execute_import_directives()
        git_repo.repo.publish()
        pages = Page.objects.all()
        self.assertGreater(len(pages), 5)
        self.assertIn(u'/en/', [p.get_absolute_url() for p in pages])
        self.assertIn(u'/en/hacking/', [p.get_absolute_url() for p in pages])

    # Check if all importe article has 'home' as parent
    def test_articletree_1file_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        git_repo = GitTestRepo()
        git_repo.repo.reset()
        git_repo.repo.add_directive('README.md', '/readme')
        git_repo.repo.execute_import_directives()
        git_repo.repo.publish()
        published_pages = Page.objects.filter(publisher_is_draft=True)
        imported_pages = published_pages.exclude(id=home.id)
        self.assertEqual(imported_pages.count(), 1)
        self.assertTrue(imported_pages[0].parent == home)

    # Check if all imported articles have 'home' as parent
    def test_articletree_1dir_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        git_repo = GitTestRepo()
        git_repo.repo.reset()
        git_repo.repo.add_directive('docs', '/')
        git_repo.repo.execute_import_directives()
        git_repo.repo.publish()
        for page in Page.objects.filter(publisher_is_draft=True):
            if page.parent is not None:
                self.assertEqual(page.parent_id, home.id)
