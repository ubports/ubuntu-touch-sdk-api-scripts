#!/usr/bin/python

from datetime import datetime
import pytz

from django.core.management.base import NoArgsCommand

from store_data.models import Architecture, Release, GadgetSnap
from ..store import api


def update_gadget_snaps():
    now = datetime.now(pytz.utc)
    for entry in api.get_oem_snap_entries():
        gadget_snap, created = GadgetSnap.objects.get_or_create(
            store_url=entry['_links']['self']['href'], name=entry['name'],
            defaults={
                'icon_url': entry['icon_url'],
                'ratings_average': entry['ratings_average'],
                'alias': entry['alias'], 'price': entry['price'], 
                'publisher': entry['publisher'], 'version': entry['version'],
                'last_updated': now})
        if not created:
            gadget_snap.last_updated = now
            gadget_snap.icon_url = entry['icon_url']
            gadget_snap.ratings_average = entry['ratings_average']
            gadget_snap.alias = entry['alias']
            gadget_snap.price: entry['price']
            gadget_snap.publisher = entry['publisher']
            gadget_snap.version = entry['version']
            gadget_snap.save()
        for arch in entry['architecture']:
            arch_ob, created = Architecture.objects.get_or_create(name=arch)
            gadget_snap.architecture.add(arch_ob)
        for release in entry['release']:
            rel_ob, created = Release.objects.get_or_create(name=release)
            gadget_snap.release.add(rel_ob)
    GadgetSnap.objects.exclude(last_updated=now).delete()


class Command(NoArgsCommand):
    help = 'Update list of gadget snaps from store.'

    def handle_noargs(self, **options):
        update_gadget_snaps()
