from django.core.management.base import NoArgsCommand

from bs4 import BeautifulSoup
import codecs
import glob
import logging
import markdown
import os
import re
import requests
import shutil
import subprocess
import tempfile

from developer_portal.models import SnappyDocsBranch

MAP = {"autopilot.md": None,
       "config.md": "config-command",
       "cross-build.md": None,
       "frameworks.md": "frameworks",
       "garbage.md": None,
       "hashes.md": None,
       "meta.md": "package-metadata",
       "oem.md": "oem",
       "package-names.md": None,
       "security.md": "security-policy"}


def get_branch_from_lp(origin, alias):
    return subprocess.call([
        'bzr', 'checkout', '--lightweight', origin, alias])


def clean_up(directory):
    shutil.rmtree(directory)


def get_published_titles():
    titles = {}
    for m in MAP:
        if MAP.get(m, False):
            url = "https://developer.ubuntu.com/en/snappy/guides/%s" % MAP[m]
            r = requests.get(url)
            soup = BeautifulSoup(r.text)
            titles[m] = soup.title.string.split(" | ")[0]
    return titles


class LocalBranch():
    def __init__(self, dirname, titles):
        self.dirname = dirname
        self.docs_path = os.path.join(self.dirname, 'docs')
        self.doc_fns = glob.glob(self.docs_path+'/*.md')
        self.titles = titles

    def import_markdown(self):
        for doc_fn in self.doc_fns:
            html = self.md_to_html(doc_fn)
            html = self.replace_links(html)
            html_fn = doc_fn.replace('.md', '.html')
            with open(html_fn, "w") as t:
                t.write(html)

    def replace_links(self, doc):
        for t in self.titles:
            url = u"https://developer.ubuntu.com/en/snappy/guides/%s" % MAP[t]
            link = u"<a href=\"%s\">%s</a>" % (url, self.titles[t])
            doc = unicode(doc.encode('utf-8'))
            doc = doc.replace(t, link)
        doc = re.sub(r"<html>\n\s<body>\n", "", doc, flags=re.MULTILINE)
        doc = re.sub(r"\s<\/body>\n<\/html>", "", doc, flags=re.MULTILINE)
        return doc

    def md_to_html(self, doc_fn):
        with codecs.open(doc_fn, 'r', encoding='utf-8') as f:
            html = markdown.markdown(f.read(), output_format="html5")
        begin = "<div class=\"row no-border\">\n<div class=\"eight-col\">\n"
        end = "</div>\n</div>"
        html = begin + html + end
        html = html.replace("<pre><code>",
                            "</div><div class=\"twelve-col\"><pre><code>")
        html = html.replace("</code></pre>",
                            "</code></pre></div><div class=\"eight-col\">")
        return html


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
    titles = get_published_titles()
    os.chdir(pwd)
    for local_branch in [a for a in glob.glob(tempdir+'/*')
                         if os.path.isdir(a)]:
        branch = LocalBranch(local_branch, titles)
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
