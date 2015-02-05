#!/usr/bin/python

from django.core.management.base import BaseCommand
from optparse import make_option

from django.conf import settings

import subprocess
import os
import sys

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Make sure The API Website database is set up properly."

    def handle(self, *args, **options):

        apidocs_perms = Permission.objects.filter(content_type__app_label='api_docs')
        authtoken_perms = Permission.objects.filter(content_type__app_label='authtoken')

        if hasattr(settings, 'ADMIN_GROUP') and settings.ADMIN_GROUP != "":
            devs, created = Group.objects.get_or_create(name=settings.ADMIN_GROUP)
            devs.permissions.add(*list(apidocs_perms))
            devs.permissions.add(*list(authtoken_perms))

        if hasattr(settings, 'EDITOR_GROUP') and settings.EDITOR_GROUP != "":
            importers, created = Group.objects.get_or_create(name=settings.EDITOR_GROUP)
            importers.permissions.add(*list(apidocs_perms))
            
