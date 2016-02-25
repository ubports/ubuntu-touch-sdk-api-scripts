import os
import shutil
import sys
import tempfile

from django.utils.text import slugify

from cms.api import create_page
from cms.models import Page
from cms.test_utils.testcases import CMSTestCase
from cms.utils.page_resolver import get_page_from_request

from ..importer import DEFAULT_LANG
from ..importer.repo import create_repo

if sys.version_info.major == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


def db_empty_page_list():
    Page.objects.all().delete()


def db_create_root_page():
    return db_add_empty_page('root')


def db_add_empty_page(title, parent=None):
    page = create_page(
        title, 'default.html', DEFAULT_LANG, slug=slugify(title),
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
        self.repo = create_repo(self.tempdir, origin, '', '')
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


def is_local_link(link):
    if link.has_attr('class') and \
       'headeranchor-link' in link.attrs['class']:
        return False
    (scheme, netloc, path, params, query, fragment) = \
        urlparse(link.attrs['href'])
    if scheme in ['http', 'https', 'mailto']:
        return False
    return True
