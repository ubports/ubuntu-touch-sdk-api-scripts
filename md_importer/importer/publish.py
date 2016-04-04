from md_importer.importer import (
    DEFAULT_LANG,
    DEFAULT_TEMPLATE,
)
from md_importer.importer.tools import remove_leading_and_trailing_slash

from cms.api import create_page, add_plugin
from cms.models import Page, Title
from cms.utils.page_resolver import get_page_from_path
from djangocms_text_ckeditor.html import clean_html

from bs4 import BeautifulSoup
import logging
import re
import os


def _compare_html(html_a, html_b):
    soup_a = BeautifulSoup(html_a, 'html5lib')
    soup_b = BeautifulSoup(html_b, 'html5lib')
    return (clean_html(soup_a.prettify()) == clean_html(soup_b.prettify()))


def slugify(filename):
    return os.path.basename(filename).replace('.md', '').replace('.html', '')


def _find_parent(full_url):
    parent_url = remove_leading_and_trailing_slash(re.sub(
        r'^\/None|{}\/'.format(DEFAULT_LANG),
        '',
        os.path.dirname(full_url)))
    parent_url = os.path.dirname(full_url)
    if not parent_url:
        root = Page.objects.get_home()
        if not root:
            return None
        return root.get_draft_object()
    parent = get_page_from_path(parent_url, draft=True)
    if not parent:
        logging.error('Parent {} not found.'.format(parent_url))
        return None
    return parent


def find_text_plugin(page):
    # We create the page, so we know there's just one placeholder
    placeholder = page.placeholders.all()[0]
    if placeholder.get_plugins():
        return (
            placeholder,
            placeholder.get_plugins()[0].get_plugin_instance()[0]
        )
    return (placeholder, None)


def update_page(page, title, full_url, menu_title=None,
                in_navigation=True, redirect=None, html=None, template=None):
    if page.get_title() != title:
        page.title = title
    if page.get_menu_title() != menu_title:
        page.menu_title = menu_title
    if page.in_navigation != in_navigation:
        page.in_navigation = in_navigation
    if page.get_redirect() != redirect:
        page.redirect = redirect
    if page.template != template:
        page.template = template
    if html:
        update = True
        (placeholder, plugin) = find_text_plugin(page)
        if plugin:
            if _compare_html(html, plugin.body):
                update = False
            elif page.get_public_object():
                (dummy, published_plugin) = \
                    find_text_plugin(page.get_public_object())
                if published_plugin:
                    if _compare_html(html, published_plugin.body):
                        update = False
            if update:
                plugin.body = html
                plugin.save()
            else:
                # Reset draft
                page.get_draft_object().revert(DEFAULT_LANG)
        else:
            add_plugin(
                placeholder, 'RawHtmlPlugin',
                DEFAULT_LANG, body=html)


def get_or_create_page(title, full_url, menu_title=None,
                       in_navigation=True, redirect=None, html=None,
                       template=DEFAULT_TEMPLATE):
    # First check if pages already exist.
    pages = Title.objects.select_related('page').filter(
        path__regex=full_url).filter(publisher_is_draft=True)
    if pages:
        page = pages[0].page
        update_page(page, title, full_url, menu_title, in_navigation,
                    redirect, html, template)
    else:
        parent = _find_parent(full_url)
        if not parent:
            return None
        slug = os.path.basename(full_url)
        page = create_page(
            title=title, template=template, language=DEFAULT_LANG, slug=slug,
            parent=parent, menu_title=menu_title, in_navigation=in_navigation,
            position='last-child', redirect=redirect)
        placeholder = page.placeholders.all()[0]
        add_plugin(placeholder, 'RawHtmlPlugin', DEFAULT_LANG, body=html)
    return page
