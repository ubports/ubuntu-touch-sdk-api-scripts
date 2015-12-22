import shutil
import tempfile

from django.utils.text import slugify

from cms.api import create_page
from cms.models import Page

from ..management.importer.repo import create_repo


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
