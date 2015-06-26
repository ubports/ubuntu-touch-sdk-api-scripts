from django.shortcuts import render_to_response
from django.template import RequestContext
from cms.models.pagemodel import Page
import json
from django.db import connection


def get_plugin_changes():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `cms_cmsplugin` ORDER BY `changed_date` DESC")
    row = cursor.fetchall()
    return row


def get_revision(plugin_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `reversion_version` WHERE `object_id_int` = %s ORDER BY `id` DESC limit 1", [plugin_id])
    row = cursor.fetchone()
    return row


def get_page_for_placeholder(ph):
    cursor = connection.cursor()
    cursor.execute("SELECT `page_id` FROM `cms_page_placeholders` WHERE `placeholder_id` = %s", [ph])
    row = cursor.fetchone()
    return row


def parse_time(time):
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    return time


class AllPages():
    all_pages = Page.objects.filter()
    dashboard_data = []
    known_paths = []
    for data in get_plugin_changes():
        rev = get_revision(data[0])
        if rev:
            content = json.loads(rev[7])
            date = data[7]
            lang = data[4].replace('-', '_')
            page_id = get_page_for_placeholder(data[1])[0]
            page = Page.objects.filter(id=page_id)[0]
            path = page.get_path()
            if path not in known_paths:
                known_paths.append(path)
                dashboard_data.append({'path': path})
            for p in dashboard_data:
                if p['path'] == path:
                    p['title'] = page.get_title()
                    if p.get(lang):
                        if date > p[lang]:
                            p[lang] = date
                    else:
                        p[lang] = date


def translations_dashboard(request):
    cms_pages = AllPages()
    return render_to_response(
        'translations_dashboard.html',
        {'cms_pages': cms_pages.dashboard_data},
        context_instance=RequestContext(request))
