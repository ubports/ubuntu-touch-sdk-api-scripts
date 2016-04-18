import os
import shutil
import sys
import tempfile

from django.utils.text import slugify

from cms.api import create_page
from cms.models import Page
from cms.test_utils.testcases import CMSTestCase
from cms.utils.page_resolver import get_page_from_request

from md_importer.models import ImportedArticle
from ..importer import (
    DEFAULT_LANG,
)
from ..importer.repo import Repo

if sys.version_info.major == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


def db_empty_page_list():
    Page.objects.all().delete()


def db_create_root_page():
    return db_add_empty_page('root')


def db_add_empty_page(title, parent=None, slug=None):
    if not slug:
        slug = slugify(title)
    page = create_page(
        title, 'default.html', DEFAULT_LANG, slug=slug,
        published=True, parent=parent)
    page.reload()
    page.publish(DEFAULT_LANG)
    return page.get_public_object()


class TestLocalBranchImport(CMSTestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        db_empty_page_list()
        self.assertEqual(Page.objects.count(), 0)
        self.root = db_create_root_page()
        self.assertFalse(self.root.publisher_is_draft)
        self.assertEqual(
            self.root.get_absolute_url(),
            '/{}/'.format(DEFAULT_LANG))

    def create_repo(self, docs_path):
        origin = os.path.join(os.path.dirname(__file__), docs_path)
        self.assertTrue(os.path.exists(origin))
        self.repo = Repo(self.tempdir, origin, '', '')
        self.fetch_retcode = self.repo.get()
        self.assertEqual(self.fetch_retcode, 0)

    def check_local_link(self, url):
        if not url.startswith('/'):
            url = '/' + url
        if not url.startswith('/{}/'.format(DEFAULT_LANG)):
            url = '/{}'.format(DEFAULT_LANG) + url
        request = self.get_request(url)
        page = get_page_from_request(request)
        return page

    def tearDown(self):
        shutil.rmtree(self.tempdir)


def check_imported_article(imported_article):
    assert imported_article is not None
    assert isinstance(imported_article, ImportedArticle)
    return True


def check_repo(repo):
    assert repo is not None
    assert isinstance(repo, Repo)
    return repo.assert_is_published()


def is_local_link(link):
    if link.has_attr('class') and \
       'headeranchor-link' in link.attrs['class']:
        return False
    (scheme, netloc, path, params, query, fragment) = \
        urlparse(link.attrs['href'])
    if scheme in ['http', 'https', 'mailto']:
        return False
    return True


class PublishedPages:
    def __init__(self):
        self.pages = None
        self.update()

    def update(self):
        self.pages = Page.objects.filter(publisher_is_draft=False)
        self.urls = [p.get_absolute_url() for p in self.pages]

    def contains_url(self, url):
        return url in self.urls

    def has_size(self, size):
        return self.pages.count() == size

    def has_at_least_size(self, size):
        return self.pages.count() >= size
