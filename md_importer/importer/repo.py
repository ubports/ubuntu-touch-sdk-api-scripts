from . import (
    SUPPORTED_ARTICLE_TYPES,
    DEFAULT_TEMPLATE,
    logger,
)
from .article import Article
from .publish import (
    IndexPage,
    ParentNotFoundException,
    slugify,
)
from .source import SourceCode

from md_importer.models import ExternalDocsBranchImportDirective

import glob
import os


class Repo:
    def __init__(self, tempdir, origin, branch_name, post_checkout_command):
        self.directives = []
        self.imported_articles = []
        self.url_map = {}
        self.titles = {}
        self.index_page = None
        # On top of the pages in imported_articles this also
        # includes index_page
        self.pages = []
        self.urls = []
        self.origin = origin
        self.branch_name = branch_name
        self.post_checkout_command = post_checkout_command
        self.branch_nick = os.path.basename(self.origin.replace('.git', ''))
        self.checkout_location = os.path.join(tempdir, self.branch_nick)

    def get(self):
        sourcecode = SourceCode(self.origin, self.checkout_location,
                                self.branch_name, self.post_checkout_command)
        if sourcecode.get() != 0:
            logger.error(
                    'Could not check out branch "{}".'.format(self.origin))
            return 1
        return 0

    def add_directive(self, import_from, write_to, advertise=True,
                      template=None):
        if template is None:
            model_info = ExternalDocsBranchImportDirective._meta
            template = model_info.get_field('template').default
        self.directives += [
            {
                'import_from': os.path.join(self.checkout_location,
                                            import_from),
                'write_to': write_to,
                'advertise': advertise,
                'template': template,
            }
        ]

    def execute_import_directives(self):
        import_list = []
        # Import single files first
        single_files = [d for d in self.directives
                        if os.path.isfile(d['import_from'])]
        # Sort by number of '/' in write_to - this should ensure that we
        # first import entries closer to the root.
        single_files.sort(
            cmp=lambda x, y:
            x['write_to'].count('/')-y['write_to'].count('/'))
        for directive in single_files:
            import_list += [
                (directive['import_from'], directive['write_to'],
                 directive['advertise'], directive['template'])
            ]
        # Import directories next
        for directive in [d for d in self.directives
                          if os.path.isdir(d['import_from'])]:
            for fn in glob.glob('{}/*'.format(directive['import_from'])):
                if fn not in [a[0] for a in import_list]:
                    import_list += [
                        (fn, os.path.join(directive['write_to'], slugify(fn)),
                         directive['advertise'], directive['template'])
                    ]
            # If we import into a namespace and don't have an index doc,
            # we need to write one.
            # XXX: Right now we just create one index doc, this will change in
            # the near future.
            if directive['write_to'] not in [x[1] for x in import_list] and \
               not self.index_page:
                try:
                    self.index_page = IndexPage(
                        title=self.branch_nick, full_url=directive['write_to'],
                        in_navigation=directive['advertise'], html='',
                        menu_title=None, template=DEFAULT_TEMPLATE)
                    self.pages.extend([self.index_page.page])
                except ParentNotFoundException:
                    return self._abort_import(
                        'Could not create fake index page at {}'.format(
                            directive['write_to']))
        # The actual import
        for entry in import_list:
            article = self._read_article(
                entry[0], entry[1], entry[2], entry[3])
            if article:
                self.imported_articles += [article]
                self.titles[article.fn] = article.title
                self.url_map[article.fn] = article
            elif os.path.splitext(entry[0])[1] in SUPPORTED_ARTICLE_TYPES:
                # In this case the article was supported but still reading
                # it failed, importing should be stopped here to avoid
                # problems.
                return self._abort_import('Reading {} failed'.format(
                    entry[0]))
        if self.index_page:
            self.index_page.add_imported_articles(
                self.imported_articles, self.origin)
        return True

    def _abort_import(self, msg):
        logger.error('Importing of {} aborted: {}.'.format(self.origin, msg))
        return False

    def _read_article(self, fn, write_to, advertise, template):
        article = Article(fn, write_to, advertise, template)
        if article.read():
            return article
        return None

    def publish(self):
        for article in self.imported_articles:
            if not article.add_to_db():
                logger.error('Publishing of {} aborted.'.format(self.origin))
                return False
            article.replace_links(self.titles, self.url_map)
        for article in self.imported_articles:
            page = article.publish()
            self.pages.extend([page])
            self.urls.extend([page.get_absolute_url()])
        if self.index_page:
            self.urls.extend([self.index_page.page.get_absolute_url()])
        return True

    def assert_is_published(self):
        for page in self.pages:
            assert page.publisher_is_draft is False
        return True

    def contains_page(self, url):
        return url in self.urls
