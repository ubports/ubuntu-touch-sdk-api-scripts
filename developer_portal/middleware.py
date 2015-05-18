# -*- coding: utf-8 -*-
"""
Middleware custom to developer.ubuntu.com
"""
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings


class CacheFriendlySessionMiddleware(SessionMiddleware):
    """
    To provide effective caching of public pages, remove the sessionid
    and csrf token from the Cookie to that Vary: Cookie doesn't cache 
    pages per-user
    """
    def process_response(self, request, response):
        response = super(CacheFriendlySessionMiddleware, self).process_response(request, response)

        #Don't do anything if it's a redirect, not found, or error
        if response.status_code != 200:
            return response
            
        #You have access to request.user in this method
        if not hasattr(request, 'user') or not request.user.is_authenticated():
            response.delete_cookie(settings.SESSION_COOKIE_NAME)
            response.delete_cookie(settings.CSRF_COOKIE_NAME)
        return response
