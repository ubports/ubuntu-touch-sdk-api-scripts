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
from django.http import HttpResponse
from django.core.urlresolvers import reverse

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
        context['solution'] = 'You will need to create a <a href="https://launchpad.net/people/+me">Launchpad profile</a> to use The Summit Scheduler'

    data = render_to_string(template_name, context,
        context_instance=RequestContext(request))
    return HttpResponse(data, status=status)
