#!/usr/bin/python

from django.core.management.base import BaseCommand
from optparse import make_option

from django.conf import settings

import subprocess
import os
import sys

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from cms.models.permissionmodels import PageUserGroup

class Command(BaseCommand):
    help = "Make sure the Developer Portal database is set up properly."

    def handle(self, *args, **options):

        all_perms = Permission.objects.filter()

        print "Creating admin user."
        admin, created = User.objects.get_or_create(username='admin')
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('password')
        admin.save()

        print "Configuring ubuntudeveloperportal group."
        devs, created = PageUserGroup.objects.get_or_create(name='ubuntudeveloperportal', defaults={'created_by': admin})
        devs.permissions.add(*list(all_perms))


