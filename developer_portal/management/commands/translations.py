#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import NoArgsCommand

import os
import glob
import subprocess
import sys

APP_NAME = "developer_portal"
project_locale_path = os.path.join(settings.PROJECT_PATH, "locale")
po_filenames = glob.glob(project_locale_path+"/*.po")

def run_manage(args):
    pwd = os.getcwd()
    os.chdir(settings.PROJECT_PATH)
    subprocess.call([sys.executable, "manage.py"]+args)
    os.chdir(pwd)


def update_template():
    run_manage(["update-template"])

def create_symlink(file_fn, symlink_fn):
    if os.path.exists(symlink_fn) and not os.path.islink(symlink_fn):
        os.remove(symlink_fn)
    if not os.path.exists(os.path.dirname(symlink_fn)):
        os.makedirs(os.path.dirname(symlink_fn))
    if not os.path.exists(symlink_fn):
        os.symlink(file_fn, symlink_fn)

def create_symlinks():
    for po_fn in po_filenames:
        locale = os.path.basename(po_fn).split(".po")[0]
        po_symlink_fn = os.path.join(project_locale_path, locale, 
                "LC_MESSAGES/django.po")
        create_symlink(po_fn, po_symlink_fn)
        # As compilemessages processes all .po files in all subdirectories
        # we better symlink the .mo files as well, to avoid getting out of
        # date
        create_symlink(po_fn.replace(".po", ".mo"), 
                       po_symlink_fn.replace(".po", ".mo"))

def compilemessages():
    run_manage(["compilemessages"])

def check():
    configured_languages = map(lambda a: a[0], settings.LANGUAGES)
    for po_fn in po_filenames:
        locale = os.path.basename(po_fn).split(".po")[0]
        locale = locale.lower().replace("_", "-")
        if locale not in configured_languages:
            print("Consider adding adding '%s' to settings.LANGUAGES." % locale)

class Command(NoArgsCommand):
    help = "Update translations template."

    def handle_noargs(self, **options):
        update_template()
        create_symlinks()
        compilemessages()
        check()
