from md_importer.importer import DEFAULT_LANG, HOME_PAGE_URL

from cms.api import create_page, add_plugin
from cms.models import Title
from djangocms_text_ckeditor.html import clean_html

import logging
import re
import os


def slugify(filename):
    return os.path.basename(filename).replace('.md', '').replace('.html', '')


def _find_parent(full_url):
    if full_url == HOME_PAGE_URL:
        # If we set up the homepage, we don't need a parent.
        return None
    parent_url = re.sub(
        r'^\/{}\/'.format(DEFAULT_LANG),
        '',
        os.path.dirname(full_url))

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
    # First check if pages already exist.
    pages = Title.objects.select_related('page').filter(
        path__regex=full_url).filter(publisher_is_draft=True)
    if pages:
        page = pages[0].page
        if page.get_title() != title:
            page.title = title
        if page.get_menu_title() != menu_title:
            page.menu_title = menu_title
        if page.in_navigation != in_navigation:
            page.in_navigation = in_navigation
        if page.get_redirect() != redirect:
            page.redirect = redirect
        if html:
            # We create the page, so we know there's just one placeholder
            placeholder = page.placeholders.all()[0]
            if placeholder.get_plugins():
                plugin = placeholder.get_plugins()[0].get_plugin_instance()[0]
                if plugin.body != clean_html(html, full=False):
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
        placeholder = page.placeholders.get()
        add_plugin(placeholder, 'RawHtmlPlugin', DEFAULT_LANG, body=html)
        placeholder = page.placeholders.all()[0]
        plugin = placeholder.get_plugins()[0].get_plugin_instance()[0]
    return page
