from md_importer.importer.repo import Repo
from .utils import (
    db_add_empty_page,
    PublishedPages,
    TestLocalBranchImport,
)

from cms.api import publish_pages


class TestSnappyWebsiteRead(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/website-test')
        self.assertTrue(isinstance(self.repo, Repo))
        self.repo.add_directive('out/get-started/as-dev/index.html', '')
        self.repo.add_directive('out/get-started/as-dev/16.04', '')
        self.assertEqual(len(self.repo.directives), 2)
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        self.assertGreater(len(self.repo.pages), 10)


class TestSnappyWebsiteIA(TestLocalBranchImport):
    def runTest(self):
        self.create_repo('data/website-test')
        snappy_page = db_add_empty_page('Snappy', self.root)
        start = db_add_empty_page(
            'Get started', parent=snappy_page, slug='start')
        as_dev = db_add_empty_page(
            'As developer', parent=start, slug='as-dev')
        page_16_04 = db_add_empty_page(
            '16.04', parent=as_dev, slug='16-04')
        publish_pages([snappy_page, start, as_dev, page_16_04])
        self.assertTrue(isinstance(self.repo, Repo))
        self.repo.add_directive('out/get-started/as-dev/index.html',
                                'snappy/start/as-dev')
        self.repo.add_directive('out/get-started/as-dev/16.04/index.html',
                                'snappy/start/as-dev/16-04')
        self.repo.add_directive('out/get-started/as-dev/16.04',
                                'snappy/start/as-dev/16-04')
        self.assertTrue(self.repo.execute_import_directives())
        self.assertTrue(self.repo.publish())
        self.assertGreater(len(self.repo.pages), 10)
        published_pages = PublishedPages()
        expected_urls = [
            '/en/',
            '/en/snappy/',
            '/en/snappy/start/',
            '/en/snappy/start/as-dev/',
            '/en/snappy/start/as-dev/16-04/',
            '/en/snappy/start/as-dev/16-04/step2-setup-azure-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-azure-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-azure-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-beaglebone-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-beaglebone-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-beaglebone-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-dragonboard-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-dragonboard-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-dragonboard-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-ec2-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-ec2-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-ec2-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-gce-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-gce-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-gce-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-intel-nuc-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-intel-nuc-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-intel-nuc-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-kvm-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-kvm-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-kvm-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-rpi2-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-rpi2-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-rpi2-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-vagrant-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-vagrant-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-vagrant-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-x86-device-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-x86-device-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-x86-device-windows/',
            '/en/snappy/start/as-dev/16-04/step3-get-familiar/',
            '/en/snappy/start/as-dev/16-04/step4-first-snap/',
            '/en/snappy/start/as-dev/16-04/step5-further-readings/',
        ]
        self.assertTrue(published_pages.has_size(len(expected_urls)))
        for url in expected_urls:
            self.assertTrue(published_pages.contains_url(url))
