from django.core.management.base import NoArgsCommand

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

from developer_portal.models import SnappyDocsBranch


class MarkdownFile():
    html = None

    def __init__(self, fn):
        self.fn = fn
        self.html_fn = self.fn.replace('.md', '.html')
        with codecs.open(self.fn, 'r', encoding='utf-8') as f:
            self.html = markdown.markdown(f.read(), output_format="html5")
        self.title = self._read_title()
        self._remove_body_and_html_tags()
        self._use_developer_site_style()

    def _read_title(self):
        soup = BeautifulSoup(self.html)
        if soup.title:
            return soup.title.text
        if soup.h1:
            return soup.h1.text
        return os.path.basename(self.fn).replace('-', ' ').title()

    def _remove_body_and_html_tags(self):
        self.html = re.sub(r"<html>\n\s<body>\n", "", self.html,
                           flags=re.MULTILINE)
        self.html = re.sub(r"\s<\/body>\n<\/html>", "", self.html,
                           flags=re.MULTILINE)

    def _use_developer_site_style(self):
        begin = u"<div class=\"row no-border\">\n<div class=\"eight-col\">\n"
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
            sluggified_fn = os.path.basename(title).replace('.md', '')
            url = u"https://developer.ubuntu.com/snappy/guides/%s" % \
                sluggified_fn
            link = u"<a href=\"%s\">%s</a>" % (url, titles[title])
            self.html = self.html.replace(os.path.basename(title), link)

    def save(self):
        with codecs.open(self.html_fn, "w", encoding='utf-8') as t:
            t.write(self.html)


def get_branch_from_lp(origin, alias):
    return subprocess.call([
        'bzr', 'checkout', '--lightweight', origin, alias])


class LocalBranch():
    titles = {}

    def __init__(self, dirname):
        self.dirname = dirname
        self.docs_path = os.path.join(self.dirname, 'docs')
        self.doc_fns = glob.glob(self.docs_path+'/*.md')
        self.md_files = []

    def import_markdown(self):
        for doc_fn in self.doc_fns:
            md_file = MarkdownFile(doc_fn)
            self.md_files += [md_file]
            self.titles[md_file.fn] = md_file.title
        for md_file in self.md_files:
            md_file.replace_links(self.titles)
            md_file.save()


def import_branches():
    if not SnappyDocsBranch.objects.count():
        logging.error('No Snappy branches registered in the '
                      'SnappyDocsBranch table yet.')
        return
    tempdir = tempfile.mkdtemp()
    pwd = os.getcwd()
    os.chdir(tempdir)
    for branch in SnappyDocsBranch.objects.all():
        if get_branch_from_lp(branch.branch_origin, branch.path_alias) != 0:
            logging.error(
                'Could not check out branch "%s".' % branch.branch_origin)
            shutil.rmtree(os.path.join(tempdir, branch.path_alias))
            break
    os.chdir(pwd)
    for local_branch in [a for a in glob.glob(tempdir+'/*')
                         if os.path.isdir(a)]:
        branch = LocalBranch(local_branch)
        branch.import_markdown()
    shutil.rmtree(tempdir)


class Command(NoArgsCommand):
    help = "Import Snappy branches for documentation."

    def handle_noargs(self, **options):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%F %T')
        import_branches()
