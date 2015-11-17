from django.core.management.base import BaseCommand
from django.core.management import call_command

from cms.api import create_page, add_plugin
from cms.models import Page, Title
from cms.utils import page_resolver

from ..importer.source import SourceCode

from bs4 import BeautifulSoup
import codecs
import glob
import logging
import markdown
import os
import re
import shutil
import sys
import tempfile

from developer_portal.models import ExternalDocsBranch

DOCS_DIRNAME = 'docs'


class MarkdownFile:
    html = None

    def __init__(self, fn, docs_namespace, slug_override=None):
        self.fn = fn
        self.docs_namespace = docs_namespace
        if slug_override:
            self.slug = slug_override
        else:
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

    def replace_links(self, titles, url_map):
        for title in titles:
            local_md_fn = os.path.basename(title)
            url = u'/'+url_map[title]
            # Replace links of the form <a href="/path/somefile.md"> first
            href = u"<a href=\"{}\">".format(url)
            md_href = u"<a href=\"{}\">".format(local_md_fn)
            self.html = self.html.replace(md_href, href)

            # Now we can replace free-standing "somefile.md" references in
            # the HTML
            link = href + u"{}</a>".format(titles[title])
            self.html = self.html.replace(local_md_fn, link)

    def publish(self):
        '''Publishes pages in their branch alias namespace.'''
        page = get_or_create_page(
            title=self.title, full_url=self.full_url, menu_title=self.title,
            html=self.html)
        page.publish('en')


class SnappyMarkdownFile(MarkdownFile):
    def __init__(self, fn, docs_namespace):
        MarkdownFile.__init__(self, fn, docs_namespace)
        self._make_snappy_mods()

    def _make_snappy_mods(self):
        # Make sure the reader knows which documentation she is browsing
        if self.release_alias != 'current':
            before = (u"<div class=\"row no-border\">\n"
                      "<div class=\"eight-col\">\n")
            after = (u"<div class=\"row no-border\">\n"
                     "<div class=\"box pull-three three-col\">"
                     "<p>You are browsing the Snappy <code>%s</code> "
                     "documentation.</p>"
                     "<p><a href=\"/snappy/guides/current/%s\">"
                     "Back to the latest stable release &rsaquo;"
                     "</a></p></div>\n"
                     "<div class=\"eight-col\">\n") % (self.release_alias,
                                                       self.slug, )
            self.html = self.html.replace(before, after)

    def publish(self):
        if self.release_alias == "current":
            # Add a guides/<page> redirect to guides/current/<page>
            page = get_or_create_page(
                title=self.title,
                full_url=self.full_url.replace('/current', ''),
                redirect="/snappy/guides/current/%s" % (self.slug))
            page.publish('en')
        else:
            self.title += " (%s)" % (self.release_alias,)
        MarkdownFile.publish(self)


def slugify(filename):
    return os.path.basename(filename).replace('.md', '')


class LocalBranch:
    titles = {}
    url_map = {}

    def __init__(self, dirname, external_branch):
        self.dirname = dirname
        self.docs_path = os.path.join(self.dirname, DOCS_DIRNAME)
        self.doc_fns = glob.glob(self.docs_path+'/*.md')
        self.md_files = []
        self.external_branch = external_branch
        self.docs_namespace = self.external_branch.docs_namespace
        self.release_alias = os.path.basename(self.docs_namespace)
        self.index_doc_title = self.release_alias.title()
        self.index_doc = self.external_branch.index_doc
        self.markdown_class = MarkdownFile

    def import_markdown(self):
        for doc_fn in self.doc_fns:
            if self.index_doc and os.path.basename(doc_fn) == self.index_doc:
                md_file = self.markdown_class(
                    doc_fn,
                    os.path.dirname(self.docs_namespace),
                    slug_override=os.path.basename(self.docs_namespace))
                self.md_files.insert(0, md_file)
            else:
                md_file = self.markdown_class(doc_fn, self.docs_namespace)
                self.md_files += [md_file]
            self.titles[md_file.fn] = md_file.title
            self.url_map[md_file.fn] = md_file.full_url
        if not self.index_doc:
            self._create_fake_index_doc()
        for md_file in self.md_files:
            md_file.replace_links(self.titles, self.url_map)

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
        for md_file in self.md_files:
            md_file.publish()

    def _create_fake_index_doc(self):
        '''Creates a fake index page at the top of the branches
           docs namespace.'''

        if self.docs_namespace == "current":
            redirect = "/snappy/guides"
        else:
            redirect = None

        in_navigation = False
        menu_title = None
        list_pages = ""
        for page in self.md_files:
            list_pages += "<li><a href=\"%s\">%s</a></li>" \
                % (os.path.basename(page.full_url), page.title)
        landing = (
            u"<div class=\"row\"><div class=\"eight-col\">\n"
            "<p>This section contains documentation for the "
            "<code>%s</code> Snappy branch.</p>"
            "<p><ul class=\"list-ubuntu\">%s</ul></p>\n"
            "<p>Auto-imported from <a "
            "href=\"https://github.com/ubuntu-core/snappy\">%s</a>.</p>\n"
            "</div></div>") % (self.release_alias, list_pages,
                               self.external_branch.branch_origin)
        page = get_or_create_page(
            title=self.index_doc_title, full_url=self.docs_namespace,
            in_navigation=in_navigation, redirect=redirect, html=landing,
            menu_title=menu_title)
        page.publish('en')


class SnappyLocalBranch(LocalBranch):
    def __init__(self, dirname, external_branch):
        LocalBranch.__init__(self, dirname, external_branch)
        self.markdown_class = SnappyMarkdownFile
        self.index_doc_title = 'Snappy documentation'
        if self.release_alias != 'current':
            self.index_doc_title += ' (%s)' % self.release_alias


def get_or_create_page(title, full_url, menu_title=None,
                       in_navigation=True, redirect=None, html=None):
    # First check if pages already exist.
    pages = Title.objects.select_related('page').filter(path__regex=full_url)
    if pages:
        page = pages[0].page
        page.title = title
        page.publisher_is_draft = True
        page.menu_title = menu_title
        page.in_navigation = in_navigation
        page.redirect = redirect
        if html:
            # We create the page, so we know there's just one placeholder
            placeholder = page.placeholders.all()[0]
            if placeholder.get_plugins():
                plugin = placeholder.get_plugins()[0].get_plugin_instance()[0]
                plugin.body = html
                plugin.save()
            else:
                add_plugin(placeholder, 'RawHtmlPlugin', 'en', body=html)
    else:
        parent_pages = Title.objects.select_related('page').filter(
            path__regex=os.path.dirname(full_url))
        if not parent_pages:
            print('Parent %s not found.' % os.path.dirname(full_url))
            sys.exit(1)
        parent = parent_pages[0].page

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
            docs_namespace__regex=selection, active=True):
        checkout_location = os.path.join(
            tempdir, os.path.basename(branch.docs_namespace))
        sourcecode = SourceCode(branch.branch_origin, checkout_location,
                                branch.post_checkout_command)
        if sourcecode.get() != 0:
            logging.error(
                'Could not check out branch "%s".' % branch.branch_origin)
            if os.path.exists(checkout_location):
                shutil.rmtree(checkout_location)
            break
        if branch.branch_origin.startswith('lp:snappy') or \
           'snappy' in branch.branch_origin.split(':')[1].split('.git')[0].split('/'):
            local_branch = SnappyLocalBranch(checkout_location, branch)
        else:
            local_branch = LocalBranch(checkout_location, branch)
        local_branch.import_markdown()
        local_branch.publish()
        local_branch.remove_old_pages()
    shutil.rmtree(tempdir)

    # https://stackoverflow.com/questions/33284171/
    call_command('cms', 'fix-tree')


class Command(BaseCommand):
    help = "Import external branches for documentation."

    def add_arguments(self, parser):
        parser.add_argument('branches', nargs='*')

    def handle(*args, **options):
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%F %T')
        branches = options['branches']
        if not branches:
            import_branches('.*')
        else:
            for b in branches:
                import_branches(b)
