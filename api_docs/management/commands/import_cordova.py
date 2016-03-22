# Import DQoc HTML from lp:ubuntu-ui-toolkit
import os, sys, re

from optparse import make_option
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.storage import get_storage_class
from django.conf import settings

from api_docs.models import *
from api_docs.importers.cordova import CordovaImporter


__all__ = (
    'Command',
)

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option(
            "-i",
            "--index",
            dest="index",
            help="QDoc .index file to import documentation from",
        ),
        make_option(
            "-r",
            "--release",
            dest="version",
            help="Version of the topic the documentation if from",
        ),
        make_option(
            "-l",
            "--lang",
            dest="lang",
            help="Target programming language (cpp or qml)",
        ),
        make_option(
            "-t",
            "--topic",
            dest="topic",
            help="Topic the documentation if from",
        ),
    )

    def handle(self, *args, **options):
        lang = options.get('lang', 'html5')
        verbosity = int(options.get('verbosity', 0))
        topic = Topic.objects.get(slug=options.get('topic'))
        language = Language.objects.get(slug=options.get('lang'), topic=topic)
        if options.get('version') == 'development':
            version = language.development_version
        elif options.get('version') == 'current':
            version = language.current_version
        else:
            version = Version.objects.get(slug=options.get('version'), language=language)
        section = None # Determined at runtime
        
        importer = CordovaImporter(topic, language, version, section, options)
        importer.run()
