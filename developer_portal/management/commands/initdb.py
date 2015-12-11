#!/usr/bin/python

from django.core.management.base import BaseCommand
from django.conf import settings

from django.contrib.auth.models import User, Permission
from cms.models.permissionmodels import PageUserGroup, GlobalPagePermission
from zinnia.models import Category


class Command(BaseCommand):
    help = "Make sure the Developer Portal database is set up properly."

    def handle(self, *args, **options):

        all_perms = Permission.objects.filter()

        print("Creating admin user.")
        admin, created = User.objects.get_or_create(username='system')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        if hasattr(settings, 'ADMIN_GROUP') and settings.ADMIN_GROUP != "":
            print("Configuring {} group.".format(settings.ADMIN_GROUP))
            admins, created = PageUserGroup.objects.get_or_create(
                name=settings.ADMIN_GROUP, defaults={'created_by': admin})
            admins.permissions.add(*list(all_perms))

            print("Configuring global permissions for group.")
            adminperms, created = GlobalPagePermission.objects.get_or_create(
                # who:
                group=admins,

                # what:
                defaults={
                    'can_change': True,
                    'can_add': True,
                    'can_delete': True,
                    'can_change_advanced_settings': True,
                    'can_publish': True,
                    'can_change_permissions': True,
                    'can_move_page': True,
                    'can_view': True,
                }
            )
            adminperms.sites.add(settings.SITE_ID)

        if hasattr(settings, 'EDITOR_GROUP') and settings.EDITOR_GROUP != "":
            print("Configuring {} group.".format(settings.EDITOR_GROUP))
            editors, created = PageUserGroup.objects.get_or_create(
                name=settings.EDITOR_GROUP, defaults={'created_by': admin})
            page_perms = Permission.objects.filter(
                content_type__app_label='cms', content_type__model='page')
            editors.permissions.add(*list(page_perms))

            print("Configuring global permissions for group.")
            editorsperms, created = GlobalPagePermission.objects.get_or_create(
                # who:
                group=editors,

                # what:
                defaults={
                    'can_change': True,
                    'can_add': True,
                    'can_delete': True,
                    'can_change_advanced_settings': False,
                    'can_publish': True,
                    'can_change_permissions': False,
                    'can_move_page': True,
                    'can_view': True,
                }
            )
            editorsperms.sites.add(settings.SITE_ID)

        print('Adding zinnia categories for the following: {}.'.format(
            ', '.join([a[0] for a in settings.LANGUAGES])))
        for lang in settings.LANGUAGES:
            if lang[1] == 'Simplified Chinese':
                Category.objects.get_or_create(title='Chinese', slug=lang[0])
            else:
                Category.objects.get_or_create(title=lang[1], slug=lang[0])
