from md_importer.importer import DEFAULT_LANG, HOME_PAGE_URL

from cms.api import create_page, add_plugin
from cms.models import Title
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
                in_navigation=True, redirect=None, html=None):
    if page.get_title() != title:
        page.title = title
    if page.get_menu_title() != menu_title:
        page.menu_title = menu_title
    if page.in_navigation != in_navigation:
        page.in_navigation = in_navigation
    if page.get_redirect() != redirect:
        page.redirect = redirect
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
                       in_navigation=True, redirect=None, html=None):
    # First check if pages already exist.
    pages = Title.objects.select_related('page').filter(
        path__regex=full_url).filter(publisher_is_draft=True)
    if pages:
        page = pages[0].page
        update_page(page, title, full_url, menu_title, in_navigation,
                    redirect, html)
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
    return page
