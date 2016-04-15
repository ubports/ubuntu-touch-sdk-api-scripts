from . import (
    DEFAULT_LANG,
    SUPPORTED_ARTICLE_TYPES,
)
from .article import Article
from .publish import (
    ArticlePage,
    ParentNotFoundException,
    slugify,
)
from .source import SourceCode

from md_importer.models import ExternalDocsBranchImportDirective

import glob
import logging
import os


class Repo:
    def __init__(self, tempdir, origin, branch_name, post_checkout_command):
        self.directives = []
        self.imported_articles = []
        self.url_map = {}
        self.titles = {}
        self.index_doc_url = None
        self.index_page = None
        self.release_alias = None
        # On top of the pages in imported_articles this also
        # includes index_page
        self.pages = []
        self.origin = origin
        self.branch_name = branch_name
        self.post_checkout_command = post_checkout_command
        branch_nick = os.path.basename(self.origin.replace('.git', ''))
        self.checkout_location = os.path.join(
            tempdir, branch_nick)
        self.index_doc_title = branch_nick
        self.article_class = Article

    def get(self):
        sourcecode = SourceCode(self.origin, self.checkout_location,
                                self.branch_name, self.post_checkout_command)
        if sourcecode.get() != 0:
            logging.error(
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
            if directive['write_to'] not in [x[1] for x in import_list]:
                self.index_doc_url = directive['write_to']
        if self.index_doc_url:
            if not self._create_fake_index_page():
                logging.error('Importing of {} aborted.'.format(self.origin))
                return False
            self.pages.extend([self.index_page.page])
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
                logging.error('Importing of {} aborted.'.format(self.origin))
                return False
        if self.index_doc_url:
            self._write_fake_index_doc()
        return True

    def _read_article(self, fn, write_to, advertise, template):
        article = self.article_class(fn, write_to, advertise, template)
        if article.read():
            return article
        return None

    def publish(self):
        for article in self.imported_articles:
            if not article.add_to_db():
                logging.error('Publishing of {} aborted.'.format(self.origin))
                return False
            article.replace_links(self.titles, self.url_map)
        for article in self.imported_articles:
            self.pages.extend([article.publish()])
        return True

    def _create_fake_index_page(self):
        '''Creates a fake index page at the top of the branches
           docs namespace.'''

        try:
            article_page = ArticlePage(
                title=self.index_doc_title, full_url=self.index_doc_url,
                in_navigation=True, html='', menu_title=None)
        except ParentNotFoundException:
            return False
        article_page.publish()
        self.index_page = article_page
        return True

    def _write_fake_index_doc(self):
        list_pages = u''
        for article in [a for a
                        in self.imported_articles
                        if a.full_url.startswith(self.index_doc_url)]:
            list_pages += u'<li><a href=\"{}\">{}</a></li>'.format(
                unicode(os.path.basename(article.full_url)),
                article.title)
        html = (
            u'<div class=\"row\"><div class=\"eight-col\">\n'
            '<p>This section contains documentation for the '
            '<code>{}</code> Snappy branch.</p>'
            '<p><ul class=\"list-ubuntu\">{}</ul></p>\n'
            '<p>Auto-imported from <a '
            'href=\"{}\">{}</a>.</p>\n'
            '</div></div>'.format(self.release_alias, list_pages,
                                  self.origin, self.origin))
        self.index_page.update(
            title=self.index_doc_title,full_url=self.index_doc_url,
            in_navigation=True, html=html, menu_title=None)
        self.index_page.publish()
