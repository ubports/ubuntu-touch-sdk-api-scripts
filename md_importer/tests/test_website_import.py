from md_importer.importer import DEFAULT_LANG
from md_importer.importer.repo import Repo
from md_importer.importer.article import Article
from .utils import (
    db_add_empty_page,
    TestLocalBranchImport,
)

from cms.api import add_plugin, publish_pages
from cms.models import Page

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
        placeholder = as_dev.placeholders.all()[0]
        add_plugin(placeholder, 'RawHtmlPlugin', DEFAULT_LANG, body='')
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
        pages = Page.objects.filter(publisher_is_draft=False)
        expected_urls = [
            '/en/',
            '/en/snappy/',
            '/en/snappy/start/',
            '/en/snappy/start/as-dev/',
            '/en/snappy/start/as-dev/16-04/',
            '/en/snappy/start/as-dev/16-04/step2-setup-beaglebone-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-beaglebone-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-beaglebone-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-dragonboard-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-dragonboard-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-dragonboard-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-intel-nuc-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-intel-nuc-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-intel-nuc-windows/',
            '/en/snappy/start/as-dev/16-04/step2-setup-rpi2-macos/',
            '/en/snappy/start/as-dev/16-04/step2-setup-rpi2-ubuntu/',
            '/en/snappy/start/as-dev/16-04/step2-setup-rpi2-windows/',
            '/en/snappy/start/as-dev/16-04/step3-get-familiar/',
            '/en/snappy/start/as-dev/16-04/step4-first-snap/',
            '/en/snappy/start/as-dev/16-04/step5-further-readings/',
        ]
        self.assertEqual(len(expected_urls), len(pages))
        for url in expected_urls:
            self.assertTrue(url in [p.get_absolute_url() for p in pages])
