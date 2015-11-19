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

    def __init__(self, tempdir, branch_origin, post_checkout_command):
        self.branch_origin = branch_origin
        self.post_checkout_command = post_checkout_command
        self.checkout_location = os.path.join(
            tempdir,
            os.path.basename(self.branch_origin.replace('.git', '')))
        self.article_class = Article
        self.directives = []
        self.imported_articles = []

    def get(self):
        sourcecode = SourceCode(self.branch_origin, self.checkout_location,
                                self.post_checkout_command)
        if sourcecode.get() != 0:
            logging.error(
                'Could not check out branch "{}".'.format(self.branch_origin))
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

    def remove_old_pages(self):
        imported_page_urls = set([md_file.full_url
                                  for md_file in self.md_files])
        index_doc = page_resolver.get_page_queryset_from_path(
            self.docs_namespace)
        db_pages = []
        pages_for_removal = []
        if len(index_doc):
            # All pages in this namespace currently in the database
            db_pages = index_doc[0].get_descendants().all()
        for db_page in db_pages:
            still_relevant = False
            for url in imported_page_urls:
                if url in db_page.get_absolute_url():
                    still_relevant = True
                    break
            # At this point we know that there's no match and the page
            # can be deleted.
            if not still_relevant:
                pages_for_removal += [db_page.id]
        # Only remove pages created by a script!
        Page.objects.filter(id__in=pages_for_removal,
                            created_by="script").delete()

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
                                  self.branch_origin))
        page = get_or_create_page(
            title=self.index_doc_title, full_url=self.index_doc,
            in_navigation=False, redirect=redirect, html=landing,
            menu_title=None)
        page.publish('en')


class SnappyLocalBranch(LocalBranch):
    def __init__(self, tempdir, branch_origin, post_checkout_command):
        LocalBranch.__init__(self, tempdir, branch_origin,
                             post_checkout_command)
        self.article_class = SnappyArticle
        self.index_doc_title = 'Snappy documentation'

    def _create_fake_index_docs(self):
        self.release_alias = os.path.basename(self.index_doc)
        if not self.index_doc.endswith('current'):
            self.index_doc_title += ' ({})'.format(self.release_alias)
        LocalBranch._create_fake_index_docs(self)
