# Import DQoc HTML from lp:ubuntu-ui-toolkit
import os, sys, re

from optparse import make_option
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.storage import get_storage_class
from django.conf import settings

from api_docs.models import *
from api_docs.importers.doxygen import DoxygenImporter


__all__ = (
    'Command',
)

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option(
            "-d",
            "--dir",
            dest="dir",
            help="Doxygen output directory to import documentation from",
        ),
        make_option(
            "-s",
            "--sections",
            dest="sections",
            help="File containing a Python dictionary mapping components to sections",
        ),
        make_option(
            "-r",
            "--release",
            dest="version",
            help="Version of the topic the documentation if from",
        ),
        make_option(
            "-t",
            "--topic",
            dest="topic",
            help="Topic the documentation if from",
        ),
        make_option(
            "-l",
            "--lang",
            dest="lang",
            help="Target programming language (cpp or qml)",
        ),
        make_option(
            "-n",
            "--namespace",
            dest="namespace",
            help="Fallback namespace to use if none is provided in the docs",
        ),
        make_option(
            "-N",
            "--strip-namespace",
            dest="strip_namespace",
            help="Strip all or part of a namespace",
        ),
        make_option(
            "-p",
            "--pages",
            dest="all_pages",
            action="store_true",
            help="Import all Pages, not just those referenced by Elements",
        ),
        make_option(
            "-P",
            "--no-pages",
            dest="no_pages",
            action="store_true",
            help="Do not import the page file",
        ),
        make_option(
            "-I",
            "--no-index",
            dest="no_index",
            action="store_true",
            help="Do not import the index.html file",
        ),
    )

    def handle(self, *args, **options):
        lang = options.get('lang', 'cpp')
        verbosity = int(options.get('verbosity', 0))
        topic = Topic.objects.get(slug=options.get('topic'))
        language = Language.objects.get(slug=options.get('lang'), topic=topic)
        if options.get('version') == 'development':
            version = language.development_version
        elif options.get('version') == 'current':
            version = language.current_version
        else:
            version = Version.objects.get(slug=options.get('version'), language=language)
        section = None # Will be determined during import
        
        importer = DoxygenImporter(topic, language, version, section, options)
        importer.run()
