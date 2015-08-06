from django.core.management.base import BaseCommand

from cms.api import create_page, add_plugin
from cms.models import Page
from cms.utils import page_resolver

from bs4 import BeautifulSoup
import codecs
import glob
import logging
import markdown
import os
import re
import shutil
import subprocess
import sys
import tempfile

from developer_portal.models import ExternalDocsBranch

DOCS_DIRNAME = 'docs'


class MarkdownFile:
    html = None

    def __init__(self, fn, docs_namespace):
        self.fn = fn
        self.docs_namespace = docs_namespace
        self.slug = slugify(self.fn)
        self.full_url = os.path.join(self.docs_namespace, self.slug)
        with codecs.open(self.fn, 'r', encoding='utf-8') as f:
            self.html = markdown.markdown(
                f.read(),
                output_format="html5",
                extensions=['markdown.extensions.tables'])
        self.release_alias = self._get_release_alias()
        self.title = self._read_title()
        self._remove_body_and_html_tags()
        self._use_developer_site_style()

    def _get_release_alias(self):
        alias = re.findall(r'/tmp/tmp\S+?/(\S+?)/%s/\S+?' % DOCS_DIRNAME,
                           self.fn)
        return alias[0]

    def _read_title(self):
        soup = BeautifulSoup(self.html, 'html5lib')
        if soup.title:
            return soup.title.text
        if soup.h1:
            return soup.h1.text
        return slugify(self.fn).replace('-', ' ').title()

    def _remove_body_and_html_tags(self):
        self.html = re.sub(r"<html>\n\s<body>\n", "", self.html,
                           flags=re.MULTILINE)
        self.html = re.sub(r"\s<\/body>\n<\/html>", "", self.html,
                           flags=re.MULTILINE)

    def _use_developer_site_style(self):
        begin = (u"<div class=\"row no-border\">"
                 "\n<div class=\"eight-col\">\n")
        end = u"</div>\n</div>"
        self.html = begin + self.html + end
        self.html = self.html.replace(
            "<pre><code>",
            "</div><div class=\"twelve-col\"><pre><code>")
        self.html = self.html.replace(
            "</code></pre>",
            "</code></pre></div><div class=\"eight-col\">")

    def replace_links(self, titles):
        for title in titles:
            url = u"/snappy/guides/%s/%s" % (
                self.release_alias, slugify(title))
            link = u"<a href=\"%s\">%s</a>" % (url, titles[title])
            self.html = self.html.replace(os.path.basename(title), link)

    def publish(self):
        '''Publishes pages in their branch alias namespace.'''
        from cms.api import create_page, add_plugin
        # FIXME: some pages are put in the wrong place!
        page = get_or_create_page(
            self.title, full_url=self.full_url, menu_title=self.title,
            html=self.html)
        page.publish('en')


class SnappyMarkdownFile(MarkdownFile):
    def __init__(self, fn, docs_namespace):
        MarkdownFile.__init__(self, fn, docs_namespace)
        self._make_snappy_mods()

    def _make_snappy_mods(self):
        # Make sure the reader knows which documentation she is browsing
        if self.release_alias != 'current':
            before = (u"<div class=\"row no-border\">"
                      "\n<div class=\"eight-col\">\n")
            after = (u"<div class=\"row no-border\">\n"
                     "<div class=\"box pull-three three-col\">"
                     "<p>You are browsing the Snappy <code>%s</code> "
                     "documentation.</p>"
                     "<p><a href=\"/snappy/guides/current/%s\">"
                     "Back to the latest stable release &rsaquo;"
                     "</a></p></div>\n"
                     "<div class=\"eight-col\">\n") % (self.release_alias,
                                                       self.slug, )
            self.html.replace(before, after)

    def publish(self):
        if self.release_alias == "current":
            # Add a guides/<page> redirect to guides/current/<page>
            page = get_or_create_page(
                self.title, full_url=self.full_url,
                redirect="/snappy/guides/current/%s" % (self.slug))
            page.publish('en')
        else:
            self.title += " (%s)" % (self.release_alias,)
        MarkdownFile.publish(self)


def slugify(filename):
    return os.path.basename(filename).replace('.md', '')


def get_branch_from_lp(origin, alias):
    return subprocess.call([
        'bzr', 'checkout', '--lightweight', origin, alias])


class LocalBranch:
    titles = {}

    def __init__(self, dirname, external_branch):
        self.dirname = dirname
        self.docs_path = os.path.join(self.dirname, DOCS_DIRNAME)
        self.doc_fns = glob.glob(self.docs_path+'/*.md')
        self.md_files = []
        self.external_branch = external_branch
        self.docs_namespace = self.external_branch.docs_namespace
        self.release_alias = os.path.basename(self.docs_namespace)
        self.index_doc_title = self.release_alias.title()
        self.markdown_class = MarkdownFile

    def import_markdown(self):
        for doc_fn in self.doc_fns:
            md_file = self.markdown_class(doc_fn, self.docs_namespace)
            self.md_files += [md_file]
            self.titles[md_file.fn] = md_file.title

    def remove_old_pages(self):
        imported_page_urls = set([md_file.full_url
                                  for md_file in self.md_files])
        index_doc = page_resolver.get_page_queryset_from_path(
            self.docs_namespace)[0]
        # All pages in this namespace currently in the database
        db_pages = index_doc.get_descendants().all()
        delete_pages = []
        for db_page in db_pages:
            for url in imported_page_urls:
                if url in db_page.get_absolute_url():
                    break
            # At this point we know that there's no match and the page
            # can be deleted.
            delete_pages += [db_page.id]
        # Only remove pages created by a script!
        Page.objects.filter(id__in=delete_pages, created_by="script").delete()

    def publish(self):
        for md_file in self.md_files:
            md_file.publish()

    def refresh_index_doc(self):
        '''Creates a index page at the top of the branches docs namespace.'''

        if self.docs_namespace == "current":
            redirect = "/snappy/guides"
        else:
            redirect = None
        landing = (u"<div class=\"row\"><div class=\"eight-col\">\n"
                   "<p>This section contains documentation for the "
                   "<code>%s</code> Snappy branch.</p>"
                   "<p>Auto-imported from <a "
                   "href=\"https://code.launchpad.net/snappy\">%s</a>.</p>\n"
                   "</div></div>") % (self.docs_namespace,
                                      self.external_branch.lp_origin)
        new_release_page = get_or_create_page(
            self.index_doc_title, full_url=self.docs_namespace,
            redirect=redirect, html=landing)
        new_release_page.publish('en')


class SnappyLocalBranch(LocalBranch):
    def __init__(self, dirname, external_branch):
        LocalBranch.__init__(self, dirname, external_branch)
        self.markdown_class = SnappyMarkdownFile
        self.index_doc_title = 'Snappy'
        if self.release_alias != 'current':
            self.index_doc_title += ' (%s)' % self.release_alias

    def import_markdown(self):
        LocalBranch.import_markdown(self)
        for md_file in self.md_files:
            md_file.replace_links(self.titles)


def get_or_create_page(title, full_url, menu_title=None,
                       in_navigation=True, redirect=None, html=None):
    pages = page_resolver.get_page_queryset_from_path(full_url)
    if pages:
        page = pages[0]
        page.title = title
        page.publisher_is_draft = True
        page.menu_title = menu_title
        page.in_navigation = in_navigation
        page.redirect = redirect
        if html:
            # We create the page, so we know there's just one placeholder
            placeholder = page.placeholders.all()[0]
            plugin = placeholder.get_plugins()[0].get_plugin_instance()[0]
            plugin.body = html
            plugin.save()
    else:
        if redirect:
            parent = None
        else:
            parent_pages = page_resolver.get_page_queryset_from_path(
                os.path.dirname(full_url))
            if not parent_pages:
                print('Parent %s not found.' % os.path.dirname(full_url))
                sys.exit(1)
            parent = parent_pages[0]
        slug = os.path.basename(full_url)
        page = create_page(
            title, "default.html", "en", slug=slug, parent=parent,
            menu_title=menu_title, in_navigation=in_navigation,
            position="last-child", redirect=redirect)
        if html:
            placeholder = page.placeholders.get()
            add_plugin(placeholder, 'RawHtmlPlugin', 'en', body=html)
    return page


def import_branches(selection):
    if not ExternalDocsBranch.objects.count():
        logging.error('No branches registered in the '
                      'ExternalDocsBranch table yet.')
        return
    tempdir = tempfile.mkdtemp()
    for branch in ExternalDocsBranch.objects.filter(
            docs_namespace__regex=selection):
        checkout_location = os.path.join(
            tempdir, os.path.basename(branch.docs_namespace))
        if get_branch_from_lp(branch.lp_origin, checkout_location) != 0:
            logging.error(
                'Could not check out branch "%s".' % branch.lp_origin)
            shutil.rmtree(checkout_location)
            break
        if branch.lp_origin.startswith('lp:snappy'):
            local_branch = SnappyLocalBranch(checkout_location, branch)
        else:
            local_branch = LocalBranch(checkout_location, branch)
        local_branch.refresh_index_doc()
        local_branch.import_markdown()
        local_branch.publish()
        local_branch.remove_old_pages()
    shutil.rmtree(tempdir)


class Command(BaseCommand):
    help = "Import external branches for documentation."

    def handle(*args, **options):
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%F %T')
        if len(args) < 2 or args[1] == "all":
            selection = '.*'
        else:
            selection = args[1]
        import_branches(selection)
