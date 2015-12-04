from cms.models import Page
from cms.utils import page_resolver

from .article import Article, SnappyArticle
from .publish import get_or_create_page, slugify
from .source import SourceCode

import glob
import logging
import os
import shutil


class LocalBranch:
    titles = {}
    url_map = {}
    index_doc_title = None
    index_doc = None
    release_alias = None

    def __init__(self, tempdir, origin, branch_name, post_checkout_command):
        self.origin = origin
        self.branch_name = branch_name
        self.post_checkout_command = post_checkout_command
        self.checkout_location = os.path.join(
            tempdir,
            os.path.basename(self.origin.replace('.git', '')))
        self.article_class = Article
        self.directives = []
        self.imported_articles = []

    def get(self):
        sourcecode = SourceCode(self.origin, self.checkout_location,
                                self.branch_name, self.post_checkout_command)
        if sourcecode.get() != 0:
            logging.error(
                'Could not check out branch "{}".'.format(self.origin))
            shutil.rmtree(self.checkout_location)
            return 1
        return 0

    def add_directive(self, import_from, write_to):
        self.directives += [
            {
                'import_from': os.path.join(self.checkout_location,
                                            import_from),
                'write_to': write_to
            }
        ]

    def execute_import_directives(self):
        import_list = []
        # Import single files first
        for directive in [d for d in self.directives
                          if os.path.isfile(d['import_from'])]:
            import_list += [
                (directive['import_from'], directive['write_to'])
            ]
        # Import directories next
        for directive in [d for d in self.directives
                          if os.path.isdir(d['import_from'])]:
            for fn in glob.glob('{}/*'.format(directive['import_from'])):
                import_list += [
                    (fn, os.path.join(directive['write_to'], slugify(fn)))
                ]
            # If we import into a namespace and don't have an index doc,
            # we need to write one.
            if directive['write_to'] not in [x[1] for x in import_list]:
                self.index_doc = directive['write_to']
        # The actual import
        for entry in import_list:
            article = self._read_article(entry[0], entry[1])
            if article:
                self.imported_articles += [article]
                self.titles[article.fn] = article.title
                self.url_map[article.fn] = article.full_url
        for article in self.imported_articles:
            article.replace_links(self.titles, self.url_map)
        if self.index_doc:
            self._create_fake_index_docs()

    def _read_article(self, fn, write_to):
        article = self.article_class(fn, write_to)
        if article.read():
            return article
        return None

    def publish(self):
        for article in self.imported_articles:
            article.publish()

    def _create_fake_index_docs(self):
        '''Creates a fake index page at the top of the branches
           docs namespace.'''

        if self.index_doc.endswith('current'):
            redirect = '/snappy/guides'
        else:
            redirect = None
        list_pages = ''
        for article in [a for a
                        in self.imported_articles
                        if a.full_url.startswith(self.index_doc)]:
            list_pages += '<li><a href=\"{}\">{}</a></li>'.format(
                os.path.basename(article.full_url), article.title)
        landing = (
            u'<div class=\"row\"><div class=\"eight-col\">\n'
            '<p>This section contains documentation for the '
            '<code>{}</code> Snappy branch.</p>'
            '<p><ul class=\"list-ubuntu\">{}</ul></p>\n'
            '<p>Auto-imported from <a '
            'href=\"https://github.com/ubuntu-core/snappy\">%s</a>.</p>\n'
            '</div></div>'.format(self.release_alias, list_pages,
                                  self.origin))
        page = get_or_create_page(
            title=self.index_doc_title, full_url=self.index_doc,
            in_navigation=False, redirect=redirect, html=landing,
            menu_title=None)
        page.publish('en')


class SnappyLocalBranch(LocalBranch):
    def __init__(self, tempdir, origin, post_checkout_command):
        LocalBranch.__init__(self, tempdir, origin,
                             post_checkout_command)
        self.article_class = SnappyArticle
        self.index_doc_title = 'Snappy documentation'

    def _create_fake_index_docs(self):
        self.release_alias = os.path.basename(self.index_doc)
        if not self.index_doc.endswith('current'):
            self.index_doc_title += ' ({})'.format(self.release_alias)
        LocalBranch._create_fake_index_docs(self)
