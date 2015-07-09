#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import NoArgsCommand

import os
import glob
import subprocess
import sys

APP_NAME = "developer_portal"
project_locale_path = settings.LOCALE_PATHS[0]
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
        po_symlink_fn = os.path.join(
            project_locale_path, locale, "LC_MESSAGES/django.po")
        create_symlink(po_fn, po_symlink_fn)


def compilemessages():
    run_manage(["compilemessages"])


def remove_toplevel_mos():
    for mo_fn in glob.glob(project_locale_path+"/*.mo"):
        locale = os.path.basename(mo_fn).split(".mo")[0]
        real_mo_fn = os.path.join(project_locale_path, locale,
                                  "LC_MESSAGES/django.mo")
        if os.path.exists(real_mo_fn):
            os.remove(mo_fn)
        else:
            # This should never happen
            print("'%s' exists, but '%s' doesn't." % (mo_fn, real_mo_fn))


def check():
    configured_languages = map(lambda a: a[0], settings.LANGUAGES)
    for po_fn in po_filenames:
        locale = os.path.basename(po_fn).split(".po")[0]
        locale = locale.lower().replace("_", "-")
        if locale not in configured_languages:
            print(
                "Consider adding '%s' to settings.LANGUAGES." % locale)
        if locale not in map(lambda a: a['code'], settings.CMS_LANGUAGES[1]):
            print(
                "Consider adding '%s' to settings.CMS_LANGUAGES." % locale)


class Command(NoArgsCommand):
    help = "Update translations template."

    def handle_noargs(self, **options):
        update_template()
        create_symlinks()
        compilemessages()
        remove_toplevel_mos()
        check()
