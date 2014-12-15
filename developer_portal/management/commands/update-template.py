# -*- coding: utf-8 -*-
#!/usr/bin/python

from django.core.management.base import NoArgsCommand

import subprocess
import os
import sys

from django.conf import settings

APP_NAME = "developer_portal"

DUMMY_LOCALE = "xx"

def update_template():
    pwd = os.getcwd()
    os.chdir(settings.PROJECT_PATH)
    subprocess.call([sys.executable, "manage.py", "makemessages", 
        "--keep-pot", "--all", "-i", "env/*", "-l", DUMMY_LOCALE])
    project_locale_path = os.path.join(settings.PROJECT_PATH, "locale")
    os.rename(os.path.join(project_locale_path,
                           "%s/LC_MESSAGES/django.po" % DUMMY_LOCALE),
              os.path.join(project_locale_path, "%s.pot" % APP_NAME))
    os.removedirs(os.path.join(project_locale_path,
                               "%s/LC_MESSAGES" % DUMMY_LOCALE))
    os.chdir(pwd)


class Command(NoArgsCommand):
    help = "Update translations template."

    def handle_noargs(self, **options):
        update_template()
