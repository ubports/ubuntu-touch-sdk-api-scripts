#!/usr/bin/python

from django.core.management.base import NoArgsCommand
from django.core.management import call_command

import os

from django.conf import settings

APP_NAME = 'developer_portal'

DUMMY_LOCALE = 'xx'


def update_template():
    call_command(
        'makemessages',
        '--keep-pot', '-i', 'env/*', '-i', 'urls.py',
        '-l', DUMMY_LOCALE)
    project_locale_path = os.path.join(settings.PROJECT_PATH, 'locale')
    os.rename(os.path.join(project_locale_path,
                           '%s/LC_MESSAGES/django.po' % DUMMY_LOCALE),
              os.path.join(project_locale_path, '%s.pot' % APP_NAME))
    os.removedirs(os.path.join(project_locale_path,
                               '%s/LC_MESSAGES' % DUMMY_LOCALE))
    old_pot_fn = os.path.join(project_locale_path, 'django.pot')
    if os.path.exists(old_pot_fn):
        os.remove(old_pot_fn)


class Command(NoArgsCommand):
    help = 'Update translations template.'

    def handle_noargs(self, **options):
        update_template()
