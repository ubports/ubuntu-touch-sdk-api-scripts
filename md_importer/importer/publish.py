from md_importer.importer import DEFAULT_LANG, HOME_PAGE_URL

from cms.api import create_page, add_plugin
from cms.models import Title

import logging
import re
import os


def slugify(filename):
    return os.path.basename(filename).replace('.md', '').replace('.html', '')


def _find_parent(full_url):
    if full_url == HOME_PAGE_URL:
        return None
    parent_url = re.sub(r'^\/en\/', '', os.path.dirname(full_url))
    if parent_url and not parent_url.endswith('/'):
        parent_url += '/'

    parent_pages = Title.objects.select_related('page').filter(
        path__regex=parent_url, language=DEFAULT_LANG).filter(
        publisher_is_draft=True)
    if not parent_pages:
        logging.error('Parent {} not found.'.format(
            parent_url))
        return None
    return parent_pages[0].page


def get_or_create_page(title, full_url, menu_title=None,
                       in_navigation=True, redirect=None, html=None):
    # Make URL explicit
    # if not full_url.startswith('/{}/'.format(DEFAULT_LANG)):
    #    full_url = os.path.join('/'+DEFAULT_LANG, full_url)
    # if not full_url.endswith('/'):
    #    full_url = full_url + '/'

    # First check if pages already exist.
    pages = Title.objects.select_related('page').filter(
        path__regex=full_url).filter(publisher_is_draft=True)
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
                add_plugin(
                    placeholder, 'RawHtmlPlugin',
                    DEFAULT_LANG, body=html)
    else:
        parent = _find_parent(full_url)
        if not parent:
            return None
        slug = os.path.basename(full_url)
        page = create_page(
            title, 'default.html', DEFAULT_LANG, slug=slug, parent=parent,
            menu_title=menu_title, in_navigation=in_navigation,
            position='last-child', redirect=redirect)
        if html:
            placeholder = page.placeholders.get()
            add_plugin(placeholder, 'RawHtmlPlugin', DEFAULT_LANG, body=html)
    return page
