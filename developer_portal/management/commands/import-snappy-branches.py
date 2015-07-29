from django.core.management.base import BaseCommand

from bs4 import BeautifulSoup
import codecs
import glob
import logging
import markdown
import os
import re
import shutil
import subprocess
import tempfile

from developer_portal.models import ExternalDocsBranch

DOCS_DIRNAME = 'docs'
SNAPPY_MARKER = 'is_snappy_branch'
RELEASE_PAGES = {}


class MarkdownFile():
    html = None

    def __init__(self, fn, is_snappy_branch=False):
        self.fn = fn
        self.slug = slugify(self.fn)
        self.is_snappy_branch = is_snappy_branch
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
        # Make sure the reader knows which documentation she is browsing
        if self.release_alias != "current" and self.is_snappy_branch:
            begin = (u"<div class=\"row no-border\">\n"
                     "<div class=\"box pull-three three-col\">"
                     "<p>You are browsing the Snappy <code>%s</code> "
                     "documentation.</p>"
                     "<p><a href=\"/snappy/guides/current/%s\">"
                     "Back to the latest stable release &rsaquo;"
                     "</a></p></div>\n"
                     "<div class=\"eight-col\">\n") % (self.release_alias,
                                                       self.slug, )
        else:
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

        page_title = self.title

        if self.is_snappy_branch and self.release_alias == "current":
            # Add a guides/<page> redirect to guides/current/<page>
            page = create_page(
                self.title, "default.html", "en",
                slug=self.slug, parent=RELEASE_PAGES['guides_page'],
                in_navigation=True, position="last-child",
                redirect="/snappy/guides/current/%s" % (self.slug))
            page.publish('en')
        else:
            page_title += " (%s)" % (self.release_alias,)

        page = create_page(
            page_title, "default.html", "en", slug=self.slug,
            menu_title=self.title, parent=RELEASE_PAGES[self.release_alias],
            in_navigation=True, position="last-child")
        placeholder = page.placeholders.get()
        add_plugin(placeholder, 'RawHtmlPlugin', 'en', body=self.html)
        page.publish('en')


def slugify(filename):
    return os.path.basename(filename).replace('.md', '')


def get_branch_from_lp(origin, alias):
    return subprocess.call([
        'bzr', 'checkout', '--lightweight', origin, alias])


class LocalBranch():
    titles = {}

    def __init__(self, dirname, external_branch):
        self.dirname = dirname
        self.docs_path = os.path.join(self.dirname, DOCS_DIRNAME)
        self.doc_fns = glob.glob(self.docs_path+'/*.md')
        self.md_files = []
        self.external_branch = external_branch
        self.docs_namespace = self.external_branch.docs_namespace
        self.is_snappy_branch = self.external_branch.lp_origin.startswith(
            'lp:snappy')

    def import_markdown(self):
        for doc_fn in self.doc_fns:
            md_file = MarkdownFile(doc_fn, self.is_snappy_branch)
            self.md_files += [md_file]
            self.titles[md_file.fn] = md_file.title
        for md_file in self.md_files:
            md_file.replace_links(self.titles)
            md_file.publish()

    def refresh_landing_page(self):
        '''Creates a branch page at snappy/guides/<branch alias>.'''
        from cms.api import create_page, add_plugin
        from cms.models import Title

        guides_page = Title.objects.filter(
            path="snappy/guides", published=True,
            language="en", publisher_is_draft=True)[0]
        RELEASE_PAGES['guides_page'] = guides_page.page

        if self.docs_namespace == "current":
            redirect = "/snappy/guides"
        else:
            redirect = None
        new_release_page = create_page(
            self.docs_namespace, "default.html", "en",
            slug=self.docs_namespace, parent=RELEASE_PAGES['guides_page'],
            in_navigation=False, position="last-child", redirect=redirect)
        placeholder = new_release_page.placeholders.get()
        landing = (u"<div class=\"row\"><div class=\"eight-col\">\n"
                   "<p>This section contains documentation for the "
                   "<code>%s</code> Snappy branch.</p>"
                   "<p>Auto-imported from <a "
                   "href=\"https://code.launchpad.net/snappy\">%s</a>.</p>\n"
                   "</div></div>") % (self.docs_namespace,
                                      self.external_branch.lp_origin)
        add_plugin(placeholder, 'RawHtmlPlugin', 'en', body=landing)
        new_release_page.publish('en')
        RELEASE_PAGES[self.docs_namespace] = new_release_page


def remove_old_pages(selection):
    # FIXME:
    # - we retrieve the old article somehow
    # - then find the Raw HTML plugin and
    # - replace the html in there
    # - also: remove pages we don't need anymore
    # - add new ones
    # - make sure we can do that for different sets of docs with
    #   different pages

    '''Removes all pages in snappy/guides, created by the importer.'''
    from cms.models import Title, Page

    pages_to_remove = []
    aliases = "|".join(
        ExternalDocsBranch.objects.values_list('docs_namespace', flat=True))
    if selection == "current":
        # Select all pages that are not in other aliases paths, this allows
        # removing existing redirections to current and current itself
        regex = "snappy/guides/(?!%s|.*/.*)|snappy/guides/current.*" % \
            (aliases)
    else:
        # Select pages that are in the selected alias path
        regex = "snappy/guides/%s.*" % (selection,)

    for g in Title.objects.select_related('page__id').filter(
            path__regex=regex):
        pages_to_remove.append(g.page.id)
    # Only remove pages created by a script!
    Page.objects.filter(id__in=pages_to_remove, created_by="script").delete()


def import_branches(selection):
    if not ExternalDocsBranch.objects.count():
        logging.error('No branches registered in the '
                      'ExternalDocsBranch table yet.')
        return
    # FIXME: Do the removal part last. Else we might end up in situations
    # where some code breaks and we stay in a state without articles.
    remove_old_pages(selection)
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
        local_branch = LocalBranch(checkout_location, branch)
        local_branch.refresh_landing_page()
        local_branch.import_markdown()
    shutil.rmtree(tempdir)


class Command(BaseCommand):
    help = "Import Snappy branches for documentation."

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
