from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from cms.models import CMSPlugin
import datetime
import pytz


def get_pages():
    dashboard_data = []
    known_paths = []
    for plugin_change in CMSPlugin.objects.filter(
            plugin_type__regex='TextPlugin|RawHtmlPlugin').order_by(
                '-changed_date'):
        date = plugin_change.changed_date
        lang = plugin_change.language.replace('-', '_')
        page = plugin_change.placeholder.page
        if not page or page.publisher_is_draft:
            continue
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
    # When an english page is missing, we still need a time to sort pages
    notime = datetime.datetime(1, 1, 1, tzinfo=pytz.timezone('UTC'))
    dashboard_data = list(reversed(sorted(
        dashboard_data, key=lambda k: k.get('en', notime))))
    return dashboard_data


@never_cache
def translations_dashboard(request):
    return render_to_response(
        'translations_dashboard.html',
        {'cms_pages': get_pages()},
        context_instance=RequestContext(request))
