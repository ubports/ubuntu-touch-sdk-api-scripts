import os
import shutil
import sys
import tempfile

from django.http.response import HttpResponseNotFound
from django.test import Client, TestCase
from django.utils.text import slugify

from cms.api import create_page, publish_pages
from cms.models import Page

from ..importer import DEFAULT_LANG
from ..importer.repo import create_repo

if sys.version_info.major == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


def db_empty_page_list():
    Page.objects.all().delete()


def db_create_home_page():
    home = create_page(
        'Test import', 'default.html', DEFAULT_LANG, slug='home')
    publish_pages([home])
    return Page.objects.all()[0]


def db_add_empty_page(title, parent):
    page = create_page(
        title, 'default.html', DEFAULT_LANG, slug=slugify(title),
        parent=parent)
    return page


class TestLocalBranchImport(TestCase):
    def setUp(self):
        db_empty_page_list()
        self.home = db_create_home_page()
        self.assertEqual(len(Page.objects.filter(publisher_is_draft=False)), 0)
        self.assertEqual(len(Page.objects.filter(publisher_is_draft=True)), 1)
        self.assertEqual(Page.objects.all()[0].get_absolute_url(), '/en/')
        self.client = Client()

    def create_repo(self, docs_path):
        self.tempdir = tempfile.mkdtemp()
        origin = os.path.join(os.path.dirname(__file__), docs_path)
        self.assertTrue(os.path.exists(origin))
        self.repo = create_repo(self.tempdir, origin, '', '')
        self.fetch_retcode = self.repo.get()
        self.assertEqual(self.fetch_retcode, 0)

    def check_local_link(self, url, pages):
        (scheme, netloc, path, params, query, fragment) = urlparse(url)
        if scheme in ['http', 'https', 'mailto']:
            # make external links pass
            self.assertTrue(True)
        else:
            url = '/{}/'.format(url)
            res = self.client.get(url)
            self.assertNotIsInstance(
                res, HttpResponseNotFound,
                msg='Link {} not found. Available pages: {}'.format(
                    url, ', '.join([p.get_absolute_url() for p in pages])))
            self.assertGreater(
                len(res.content), 0,
                msg='Page {} is empty.'.format(url))

    def tearDown(self):
        shutil.rmtree(self.tempdir)
