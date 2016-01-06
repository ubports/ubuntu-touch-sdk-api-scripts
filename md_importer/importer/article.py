from bs4 import BeautifulSoup
import codecs
import logging
import markdown
import os
import re

from .publish import get_or_create_page, slugify


class Article:
    html = None
    page = None
    title = ""

    def __init__(self, fn, write_to):
        self.fn = fn
        self.write_to = slugify(self.fn)
        self.full_url = write_to
        self.slug = os.path.basename(self.full_url)

    def read(self):
        with codecs.open(self.fn, 'r', encoding='utf-8') as f:
            if self.fn.endswith('.md'):
                self.html = markdown.markdown(
                    f.read(),
                    output_format='html5',
                    extensions=['pymdownx.github'])
            elif self.fn.endswith('.html'):
                self.html = f.read()
            else:
                logging.error("Don't know how to interpret '{}'.".format(
                    self.fn))
                return False
        self.title = self._read_title()
        self._remove_body_and_html_tags()
        self._use_developer_site_style()
        return True

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
        soup = BeautifulSoup(self.html, 'html5lib')
        for link in soup.find_all('a'):
            for title in titles:
                if link.attrs['href'] == os.path.basename(title):
                    link.attrs['href'] = url_map[title].full_url
        self.html = soup.prettify()

    def add_to_db(self):
        '''Publishes pages in their branch alias namespace.'''
        self.page = get_or_create_page(
            title=self.title, full_url=self.full_url, menu_title=self.title,
            html=self.html)
        self.full_url = self.page.get_absolute_url()


class SnappyArticle(Article):
    release_alias = None

    def read(self):
        if not Article.read(self):
            return False
        self.release_alias = re.findall(r'snappy/guides/(\S+?)/\S+?',
                                        self.full_url)[0]
        self._make_snappy_mods()
        return True

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

    def add_to_db(self):
        if self.release_alias == "current":
            # Add a guides/<page> redirect to guides/current/<page>
            get_or_create_page(
                title=self.title,
                full_url=self.full_url.replace('/current', ''),
                redirect="/snappy/guides/current/{}".format(self.slug))
        else:
            self.title += " (%s)" % (self.release_alias,)
        Article.add_to_db(self)
