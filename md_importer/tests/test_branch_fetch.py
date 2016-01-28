import os
import shutil
import tempfile

from django.test import TestCase

from md_importer.importer.repo import create_repo, Repo


class TestBranchFetch(TestCase):
    def test_git_fetch(self):
        tempdir = tempfile.mkdtemp()
        repo = create_repo(
            tempdir,
            'https://github.com/ubuntu-core/snapcraft.git',
            'master',
            '')
        ret = repo.get()
        shutil.rmtree(tempdir)
        self.assertEqual(ret, 0)
        self.assertTrue(isinstance(repo, Repo))

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
