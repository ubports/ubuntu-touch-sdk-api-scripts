import os
import shutil
import tempfile

from django.utils.text import slugify

from cms.api import create_page, publish_pages
from cms.models import Page

from ..importer import DEFAULT_LANG
from ..importer.repo import create_repo


class SnapcraftTestRepo():
    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.repo = create_repo(
            self.tempdir,
            os.path.join(os.path.dirname(__file__), 'data/snapcraft-test'),
            '',
            '')
        self.fetch_retcode = self.repo.get()

    def __del__(self):
        shutil.rmtree(self.tempdir)


class SnappyTestRepo():
    def __init__(self):
        self.tempdir = tempfile.mkdtemp()
        self.repo = create_repo(
            self.tempdir,
            os.path.join(os.path.dirname(__file__), 'data/snappy-test'),
            '',
            '')
        self.fetch_retcode = self.repo.get()

    def __del__(self):
        shutil.rmtree(self.tempdir)


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
