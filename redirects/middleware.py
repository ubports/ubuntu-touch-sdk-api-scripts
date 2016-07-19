# -*- coding: utf-8 -*-
"""
Middleware for handling redirects
"""
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings
from .models import PathMatchRedirect

class Redirect404Middleware(SessionMiddleware):
    """
    Only attempt redirects in response to a request returning a 404
    response code.
    """
    def process_response(self, request, response):
        response = super(Redirect404Middleware, self).process_response(request, response)

        # Don't do anything unless it's 404 (not found)
        if response.status_code != 404:
            return response
            
        try_redirects = PathMatchRedirect.objects.all().order_by("-precedence")
        for redirect in try_redirects:
            if request.path.startswith(redirect.match):
                response.status_code = 301 # permanent redirect
                if redirect.preserve_extra:
                    new_path = redirect.replace + request.path[len(redirect.match):]
                else:
                    new_path = redirect.replace

                response['Location'] = new_path
                break;

        return response
        

