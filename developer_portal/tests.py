import tempfile

from django.test import TestCase
from cms.api import create_page
from cms.models import Page

from management.importer.local_branch import LocalBranch


class TestBranchFetch(TestCase):
    def test_fetch(self):
        tempdir = tempfile.mkdtemp()
        l = LocalBranch(
            tempdir,
            'https://github.com/ubuntu-core/snapcraft.git',
            'master',
            '')
        self.assertEqual(l.get(), 0)

    def test_simple_import(self):
        home = create_page('Test import', 'default.html', 'en', slug='home')
        home.publish('en')
        tempdir = tempfile.mkdtemp()
        l = LocalBranch(
            tempdir,
            'https://github.com/ubuntu-core/snapcraft.git',
            'master',
            '')
        l.get()
        l.add_directive('docs', '/')
        l.execute_import_directives()
        l.publish()
        pages = Page.objects.all()
        self.assertGreater(len(pages), 3)
