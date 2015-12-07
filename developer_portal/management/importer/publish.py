from cms.api import create_page, add_plugin
from cms.models import Page, Title
from cms.utils import page_resolver

import logging
import os
import sys


def slugify(filename):
    return os.path.basename(filename).replace('.md', '').replace('.html', '')


def get_or_create_page(title, full_url, menu_title=None,
                       in_navigation=True, redirect=None, html=None):
    # First check if pages already exist.
    pages = Title.objects.select_related('page').filter(path__regex=full_url)
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
            path__regex=os.path.dirname(full_url))
        if not parent_pages:
            logging.error('Parent %s not found.'.format(
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


def remove_old_pages(imported_articles):
    imported_page_urls = set([article.full_url
                              for article in imported_articles])
    index_doc = page_resolver.get_page_queryset_from_path(
        self.docs_namespace)
    db_pages = []
    pages_for_removal = []
    if len(index_doc):
        # All pages in this namespace currently in the database
        db_pages = index_doc[0].get_descendants().all()
    for db_page in db_pages:
        still_relevant = False
        for url in imported_page_urls:
            if url in db_page.get_absolute_url():
                still_relevant = True
                break
        # At this point we know that there's no match and the page
        # can be deleted.
        if not still_relevant:
            pages_for_removal += [db_page.id]
    # Only remove pages created by a script!
    Page.objects.filter(id__in=pages_for_removal,
                        created_by="script").delete()
