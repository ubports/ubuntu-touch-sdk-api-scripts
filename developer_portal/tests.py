import os
import shutil
import tempfile

from django.test import TestCase
from django.utils.text import slugify

from cms.api import create_page, publish_pages
from cms.models import Page

from management.importer.repo import create_repo, Repo, SnappyRepo
from management.importer.article import Article, SnappyArticle


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


# We are going to re-use this one, so we don't have to checkout the git
# repo all the time.
class SnapcraftTestRepo():
    __metaclass__ = Singleton

    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.repo = create_repo(
            self.tempdir,
            'https://github.com/ubuntu-core/snapcraft.git',
            'master',
            '')
        self.fetch_retcode = self.repo.get()


class SnappyTestRepo():
    __metaclass__ = Singleton

    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.repo = create_repo(
            self.tempdir,
            'https://github.com/ubuntu-core/snappy.git',
            'master',
            '')
        self.fetch_retcode = self.repo.get()


def tearDownModule():
    shutil.rmtree(SnapcraftTestRepo().tempdir)
    shutil.rmtree(SnappyTestRepo().tempdir)


def db_empty_page_list():
    Page.objects.all().delete()


def db_create_home_page():
    home = create_page('Test import', 'default.html', 'en', slug='home')
    return home


def db_add_empty_page(title, parent):
    page = create_page(title, 'default.html', 'en', slug=slugify(title),
                       parent=parent)
    return page


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


class TestBranchFetch(TestCase):
    def test_git_fetch(self):
        snapcraft = SnapcraftTestRepo()
        snapcraft.repo.reset()
        self.assertEqual(snapcraft.fetch_retcode, 0)
        self.assertTrue(isinstance(snapcraft.repo, Repo))

    def test_bzr_fetch(self):
        tempdir = tempfile.mkdtemp()
        repo = create_repo(
            tempdir,
            'lp:snapcraft',  # outdated, but should work for testing
            '',
            '')
        ret = repo.get()
        shutil.rmtree(tempdir)
        self.assertEqual(ret, 0)
        self.assertTrue(isinstance(repo, Repo))

    def test_post_checkout_command(self):
        tempdir = tempfile.mkdtemp()
        repo = create_repo(
            tempdir,
            'lp:snapcraft',
            '',
            'touch something.html'
        )
        ret = repo.get()
        self.assertEqual(ret, 0)
        self.assertTrue(os.path.exists(
            os.path.join(repo.checkout_location, 'something.html')))
        shutil.rmtree(tempdir)


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
        self.assertTrue(snapcraft.repo.imported_articles[0].page.parent == home)

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


class TestSnappyImport(TestCase):
    def test_snappy_devel_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        snappy_page = db_add_empty_page('Snappy', home)
        guides = db_add_empty_page('Guides', snappy_page)
        snappy = SnappyTestRepo()
        snappy.repo.reset()
        self.assertEqual(snappy.fetch_retcode, 0)
        self.assertTrue(isinstance(snappy.repo, SnappyRepo))
        snappy.repo.add_directive('docs', '/snappy/guides/devel')
        snappy.repo.execute_import_directives()
        snappy.repo.publish()
        self.assertGreater(len(snappy.repo.imported_articles), 0)
        for article in snappy.repo.imported_articles:
            self.assertTrue(isinstance(article, SnappyArticle))
        pages = Page.objects.filter(publisher_is_draft=True)
        self.assertEqual(pages.filter(parent=guides).count(), 1)
        devel = pages.filter(parent=guides)[0]
        for page in Page.objects.filter(publisher_is_draft=True):
            if page not in [home, snappy_page, guides, devel]:
                self.assertEqual(page.parent, devel)

    def test_snappy_current_import(self):
        db_empty_page_list()
        home = db_create_home_page()
        snappy_page = db_add_empty_page('Snappy', home)
        guides = db_add_empty_page('Guides', snappy_page)
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
        pages = Page.objects.filter(publisher_is_draft=True)
        current_search = [
            a for a in pages.filter(parent=guides)
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
