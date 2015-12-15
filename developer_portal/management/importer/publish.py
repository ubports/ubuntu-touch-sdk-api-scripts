from cms.api import create_page, add_plugin
from cms.models import Title

import logging
import os
import sys

# XXX: use this once we RawHTML plugins don't strip comments (LP: #1523925)
START_TEXT = """
<!--
branch id: {}

THIS PAGE IS AUTOMATICALLY UPDATED.
DON'T EDIT IT - CHANGES WILL BE OVERWRITTEN.
-->
"""


def slugify(filename):
    return os.path.basename(filename).replace('.md', '').replace('.html', '')


def get_or_create_page(title, full_url, menu_title=None,
                       in_navigation=True, redirect=None, html=None):
    # First check if pages already exist.
    if full_url.startswith('/'):
        full_url = full_url[1:]
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
                add_plugin(placeholder, 'RawHtmlPlugin', 'en', body=html)
    else:
        parent_pages = Title.objects.select_related('page').filter(
            path__regex=os.path.dirname(full_url)).filter(
            publisher_is_draft=True)
        if not parent_pages:
            logging.error('Parent {} not found.'.format(
                os.path.dirname(full_url)))
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
