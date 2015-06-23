#!/usr/bin/python

from datetime import datetime
import pytz

from django.core.management.base import NoArgsCommand

from store_data.models import Architecture, Release, GadgetSnap
from ..store import api


def add_architecture(architecture):
    arch_ob, created = Architecture.objects.get_or_create(name=architecture)
    if created:
        arch_ob.save()
    return arch_ob


def add_release(release):
    rel_ob, created = Release.objects.get_or_create(name=release)
    if created:
        rel_ob.save()
    return rel_ob


def update_gadget_snaps():
    now = datetime.now(pytz.utc)
    for entry in api.get_oem_snap_entries():
        gadget_snap, created = GadgetSnap.objects.get_or_create(
            icon_url=entry['icon_url'], name=entry['name'],
            ratings_average=entry['ratings_average'], alias=entry['alias'],
            price=entry['price'], publisher=entry['publisher'],
            store_url=entry['_links']['self']['href'],
            version=entry['version'], last_updated=now)
        if not created:
            gadget_snap.last_updated = now
        for arch in entry['architecture']:
            arch_ob = add_architecture(arch)
            gadget_snap.architecture.add(arch_ob)
        for release in entry['release']:
            rel_ob = add_release(release)
            gadget_snap.release.add(rel_ob)
    GadgetSnap.objects.exclude(last_updated=now).delete()


class Command(NoArgsCommand):
    help = 'Update list of gadget snaps from store.'

    def handle_noargs(self, **options):
        update_gadget_snaps()
