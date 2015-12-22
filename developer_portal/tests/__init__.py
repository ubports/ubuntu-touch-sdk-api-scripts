import shutil

from utils import SnapcraftTestRepo, SnappyTestRepo


def tearDownModule():
    shutil.rmtree(SnapcraftTestRepo().tempdir)
    shutil.rmtree(SnappyTestRepo().tempdir)
