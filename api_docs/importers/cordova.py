# Import DQoc HTML from lp:ubuntu-ui-toolkit
import os

import simplejson

from django.core.files import File
from django.core.files.storage import get_storage_class

from ..models import *
from . import Importer


__all__ = (
    'CordovaImporter',
)

SECTIONS = {
    'org.apache.cordova.battery-status': 'Device and Sensors',
    'org.apache.cordova.camera': 'Device and Sensors',
#    'org.apache.cordova.contacts': 'Platform Services',
    'org.apache.cordova.device': 'Device and Sensors',
    'org.apache.cordova.device-motion': 'Device and Sensors',
    'org.apache.cordova.dialogs': 'Graphical Interface',
#    'org.apache.cordova.geolocation': 'Platform Services',
    'org.apache.cordova.globalization': 'Language Types',
    'org.apache.cordova.inappbrowser': 'Platform Services',
    'org.apache.cordova.media': 'Multimedia',
    'org.apache.cordova.media-capture': 'Device and Sensors',
    'org.apache.cordova.network-information': 'Platform Services',
    'org.apache.cordova.splashscreen': 'Graphical Interface',
    'org.apache.cordova.vibration': 'Device and Sensors',
}

class CordovaImporter(Importer):

    SOURCE_FORMAT = "cordova"
    
    def __init__(self, *args, **kwargs):
        super(CordovaImporter, self).__init__(*args, **kwargs)
        self.source = self.options.get('index')
        self.DOC_ROOT = os.path.dirname(self.source)
        self.in_supported_platforms = False
        self.in_quirks = False

    def parse_line(self, line, source_filename, element_fullname):
        if '<h3>Supported Platforms</h3>\n' in line:
            self.in_supported_platforms = True
            return ''
        if self.in_supported_platforms:
            if '</ul>' in line:
                self.in_supported_platforms = False
                line.replace('</ul>', '', 1)
            else:
                return ''
        if 'Quirks</h3>\n' in line or 'Quirk</h3>\n' in line:
            self.in_quirks = True
            return ''
        if self.in_quirks:
            if '<h3>' in line or '<h2>' in line or '<h1>' in line:
                self.in_quirks = False
            else:
                return ''
        clean_line = super(CordovaImporter, self).parse_line(line, source_filename, element_fullname)
        return clean_line
        
    def parse_filename(self, filename):
        pass
        
    def parse_href(self, href):
        pass
        
    def run(self):
        if not os.path.exists(self.source):
            print "Source index not found"
            exit(1)
            
        datafile = open(self.source)
        tree = simplejson.load(datafile)
        datafile.close()

        self.PRIMARY_NAMESPACE = 'org.apache.cordova'

        # Map document filenames to QML class names
        for jsclass in tree:
            classname = self.parse_classname(jsclass.get('term'))
            if classname.startswith(self.PRIMARY_NAMESPACE):
                self.class_map[jsclass.get('url')] = classname
            else:
                pass#self.page_map[jsclass.get('url')] = classname

        # Import YUI class documentation
        for jsclass in tree:
            ns_name = None
            fullname = None
            classname = None
            classpath = self.parse_classname(jsclass.get('term'))
            # Remove module name part of the classname
            if classpath.startswith(self.PRIMARY_NAMESPACE):
                fullname = classpath[len(self.PRIMARY_NAMESPACE)+1:].title()
                if '.' in fullname:
                    classname = fullname.split('.')[-1]
                else:
                    classname = fullname
                ns_name = classpath
            
            if classpath not in SECTIONS:
                continue
                
            self.section, section_created = Section.objects.get_or_create(name=SECTIONS[classpath], topic_version=self.version)
            
            if ns_name is not None:
                namespace, created = Namespace.objects.get_or_create(name=ns_name, platform_section=self.section)
            else:
                namespace = None

            self.import_module(namespace, classname, jsclass.get('url'))
            
    def import_module(self, namespace, classname, source_doc):
            
        doc_file = os.path.join(self.DOC_ROOT, source_doc)
        doc_handle = open(doc_file)
        doc_data = doc_handle.readlines()
        doc_handle.close()
        
        if isinstance(namespace.name, unicode):
            fullname = unicode.encode(namespace.name, 'ascii')
        else:
            fullname = namespace.name
        element, created = Element.objects.get_or_create(name=classname, fullname=fullname, section=self.section, namespace=namespace)
            
        if self.verbosity >= 1:
            print 'Element: ' + element.fullname

        doc_start = 2
        doc_end = -2
        for i, line in enumerate(doc_data):
            if '<h1><a name="%s">' % fullname in line:
                doc_start = i+2
            if '<!-- Functionality and Syntax Highlighting -->' in line:
                doc_end = i-3
        if self.verbosity >= 3:
            print "Doc range: %s:%s" % (doc_start, doc_end)
        try:
            # Change the content of the docs 
            cleaned_data = ''
            for line in doc_data[doc_start:doc_end]:
                if line == '' or line == '\n':
                    continue
                line = self.parse_line(line, source_doc, fullname)
                if isinstance(line, unicode):
                    line = line.encode('ascii', 'replace')
                cleaned_data += line
                
            element.data = cleaned_data
        except Exception, e:
            print "Parsing content failed:"
            print e
            import pdb; pdb.set_trace()
            
        element.source_file = os.path.basename(doc_file)
        element.source_format = "cordova"
        element.save()

    def import_page(self, pagehref, pagename, pagetitle, ns_name):
            if pagename.endswith('.html'):
                pagename = pagename[:-5]

            if ns_name is not None:
                namespace, created = Namespace.objects.get_or_create(name=ns_name, platform_section=self.section)
            else:
                namespace = None
                
            if namespace is not None:
                fullname = namespace.name + '.' + pagename
            else:
                fullname = pagename
            page, created = Page.objects.get_or_create(slug=pagename, fullname=fullname, title=pagetitle, section=self.section, namespace=namespace)

            if self.verbosity >= 1:
                print 'Page: ' + page.slug
            
            doc_file = os.path.join(self.DOC_ROOT, pagehref)
            doc_handle = open(doc_file)
            doc_data = doc_handle.readlines()
            doc_handle.close()
            
            doc_start = 2
            doc_end = -2
            for i, line in enumerate(doc_data):
                if '<div id="main" class="yui3-u">' in line:
                    doc_start = i+2
                if '<script src="../assets/vendor/prettify/prettify-min.js"></script>' in line:
                    doc_end = i-4
            if self.verbosity >= 3:
                print "Doc range: %s:%s" % (doc_start, doc_end)

            try:
                # Change the content of the docs 
                cleaned_data = ''
                for line in doc_data[doc_start:doc_end]:
                    if line == '' or line == '\n':
                        continue
                    if '<h1 class="title">' in line:
                        continue
                    line = self.parse_line(line, pagehref, fullname)
                    if isinstance(line, unicode):
                        line = line.encode('ascii', 'replace')
                    cleaned_data += line
                    
                page.data = cleaned_data
            except Exception, e:
                print "Parsing content failed:"
                print e
                #continue
                #import pdb; pdb.set_trace()
            page.source_file = os.path.basename(doc_file)
            page.source_format = "cordova"
            page.order_index = page_order_index
            page.save()
            
