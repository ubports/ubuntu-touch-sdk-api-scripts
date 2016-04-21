from bs4 import BeautifulSoup
import codecs
import markdown
import os
import re
import sys

from . import (
    DEFAULT_LANG,
    DEFAULT_TEMPLATE,
    logger,
    MARKDOWN_EXTENSIONS,
    SUPPORTED_ARTICLE_TYPES,
)
from .publish import (
    ArticlePage,
    ParentNotFoundException,
    slugify,
)

if sys.version_info.major == 2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


class Article:
    def __init__(self, fn, write_to, advertise=True,
                 template=DEFAULT_TEMPLATE):
        self.html = None
        self.article_page = None
        self.title = ""
        self.fn = fn
        self.write_to = slugify(self.fn)
        self.full_url = write_to
        self.slug = os.path.basename(self.full_url)
        self.links_rewritten = False
        self.local_images = []
        self.advertise = advertise
        self.template = template

    def _find_local_images(self):
        '''Local images are currently not supported.'''
        soup = BeautifulSoup(self.html, 'html5lib')
        for img in soup.find_all('img'):
            if img.has_attr('src'):
                (scheme, netloc, path, params, query, fragment) = \
                    urlparse(img.attrs['src'])
                if scheme not in ['http', 'https']:
                    self.local_images.extend([img.attrs['src']])

    def read(self):
        if os.path.splitext(self.fn)[1] not in SUPPORTED_ARTICLE_TYPES:
            logger.error("Don't know how to interpret '{}'.".format(
                self.fn))
            return False
        with codecs.open(self.fn, 'r', encoding='utf-8') as f:
            if self.fn.endswith('.md'):
                self.html = markdown.markdown(
                    f.read(),
                    output_format='html5',
                    extensions=MARKDOWN_EXTENSIONS)
            elif self.fn.endswith('.html'):
                self.html = f.read()
        self._find_local_images()
        if self.local_images:
            logger.error('Found the following local image(s): {}'.format(
                ', '.join(self.local_images)
            ))
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
        for regex in [
            # These are added by markdown.markdown
            r'\s*<html>\s*<body>\s*',
            r'\s*<\/body>\s*<\/html>\s*',
            # This is added by BeautifulSoup.prettify
            r'\s*<html>\s*<head>\s*<\/head>\s*<body>\s*',
        ]:
            self.html = re.sub(regex, '', self.html,
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
            if not link.has_attr('class') or \
               'headeranchor-link' not in link.attrs['class']:
                for title in titles:
                    if title.endswith(link.attrs['href']) and \
                       link.attrs['href'] != url_map[title].full_url:
                        link.attrs['href'] = url_map[title].full_url
                        if not link.attrs['href'].startswith('/'):
                            link.attrs['href'] = '/' + link.attrs['href']
                        self.links_rewritten = True
        if self.links_rewritten:
            self.html = soup.prettify()
            self._remove_body_and_html_tags()

    def add_to_db(self):
        '''Publishes pages in their branch alias namespace.'''
        try:
            self.article_page = ArticlePage(
                title=self.title, full_url=self.full_url,
                menu_title=self.title, html=self.html,
                in_navigation=self.advertise, template=self.template)
        except ParentNotFoundException:
            return False
        self.full_url = re.sub(
            r'^\/None\/', '/{}/'.format(DEFAULT_LANG),
            self.article_page.draft.get_absolute_url())
        return True

    def publish(self):
        if self.links_rewritten:
            self.article_page.update(
                title=self.title, full_url=self.full_url,
                menu_title=self.title, html=self.html,
                in_navigation=self.advertise, template=self.template)
        self.article_page.publish()
        return self.article_page.page
