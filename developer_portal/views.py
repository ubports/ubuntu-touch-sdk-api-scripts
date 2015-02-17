# The Summit Scheduler web application
# Copyright (C) 2008 - 2013 Ubuntu Community, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render_to_response, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth import logout
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from django_openid_auth.signals import openid_login_complete

try:
    from django_openid_auth.exceptions import (
        MissingPhysicalMultiFactor,
        MissingUsernameViolation,
    )

except ImportError:
    MissingPhysicalMultiFactor = None
    MissingUsernameViolation = None

def login_failure(request, message, status=403,
        template_name='login_failure.html',
        exception=None):
    """Render an error page to the user."""
    context = {
        'message': message,
        'exception': exception,
    }
    if isinstance(exception, MissingPhysicalMultiFactor):
        context['solution'] = 'Try logging in again using your Yubikey'
    elif isinstance(exception, MissingUsernameViolation):
        context['solution'] = _('You will need to create a <a href="https://launchpad.net/+login">Launchpad profile</a> to use the developer site')

    data = render_to_string(template_name, context,
        context_instance=RequestContext(request))
    return HttpResponse(data, status=status)

def promote_staff(request, openid_response,**kwargs):
    try:
        if not request.user.is_staff and (settings.ADMIN_GROUP in request.POST['openid.lp.is_member'] or settings.EDITOR_GROUP in request.POST['openid.lp.is_member']):
            request.user.is_staff = True
    except:
        request.user.is_staff = False
    request.user.save()
    
def listen_for_login():
    openid_login_complete.connect(promote_staff)

def site_logout(request):
    logout(request)
    if "next" in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    return HttpResponseRedirect('/')
    
from cms.utils import get_template_from_request, get_language_code
from cms.utils.i18n import get_language_list
from cms.models.pagemodel import Page
from django.utils.translation import get_language
from django.contrib.sites.models import Site
from django.template.response import TemplateResponse
import api_docs.models
def search(request):
    query = request.GET.get('q', None)
    if query is None or query == '':
        return HttpResponseRedirect('/')

    current_language = request.REQUEST.get('language', None)
    if current_language:
        current_language = get_language_code(current_language)
    if current_language is None:
        current_language = get_language_code(getattr(request, 'LANGUAGE_CODE', None))
        if current_language:
            current_language = get_language_code(current_language)
    if current_language is None:
        current_language = get_language_code(get_language())

    site = Site.objects.get_current()
    pages = Page.objects.public().published(site=site)
    cms_page_matches = pages.filter(title_set__title__icontains=query, title_set__language=current_language).distinct()

    current_versions = []
    for language in api_docs.models.Language.objects.all():
        current_versions.append(language.current_version)
    api_element_matches = api_docs.models.Element.objects.filter(section__topic_version__in=current_versions).filter(Q(fullname__icontains=query)|Q(description__icontains=query)).order_by('section', 'fullname')

    api_page_matches = api_docs.models.Page.objects.filter(Q(fullname__icontains=query)|Q(description__icontains=query))
    
    context = {
        'cms_page_matches': cms_page_matches, 
        'api_element_matches': api_element_matches, 
        'api_page_matches': api_page_matches, 
        'query': query,
    }
    return TemplateResponse(request, 'search_results.html', RequestContext(request, context))
