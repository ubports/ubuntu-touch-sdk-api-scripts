# Import DQoc HTML from lp:ubuntu-ui-toolkit
import os

import xml.etree.ElementTree as ET

from django.core.files import File
from django.core.files.storage import get_storage_class

from ..models import *
from . import Importer


__all__ = (
    'QDocImporter',
)

class QDocImporter(Importer):

    SOURCE_FORMAT = "qdoc"
    
    def __init__(self, *args, **kwargs):
        super(QDocImporter, self).__init__(*args, **kwargs)
        self.source = self.options.get('index')
        self.DOC_ROOT = os.path.dirname(self.source)

    def parse_namespace(self, namespace):
        if namespace == 'QtQuick' and self.source.endswith('/qtqml.index'):
            namespace = 'QtQml'
        return super(QDocImporter, self).parse_namespace(namespace)
        
    def run(self):

        if not self.section:
            print "Missing section: %s" % self.options.get('section')
            exit(2)

        if not os.path.exists(self.source):
            print "Source index file not found"
            exit(1)
            
        tree = ET.parse(self.source)
        root = tree.getroot()
        
        if self.language.slug == 'qml':
            class_node = 'qmlclass'
            class_module = 'qml-module-name'
        elif self.language.slug == 'cpp':
            class_node = 'class'
            class_module = 'module'
        else:
            print "Unknown language: %s" % self.language.name
            exit(2)
            
        # Map document filenames to QML class names
        self.class_map = {}
        for qmlclass in root.find('namespace').iter(class_node):
            classname = self.parse_classname(qmlclass.get('name'))
            ns_name = self.parse_namespace(qmlclass.get(class_module, None))
            if not self.PRIMARY_NAMESPACE:
                self.PRIMARY_NAMESPACE = ns_name
            if ns_name is not None:
                self.class_map[qmlclass.get('href')] = ns_name+'.'+classname
            else:
                self.class_map[qmlclass.get('href')] = classname

        # Keep track of pages that are references so they can be imported later
        self.page_refs = {}
        
        # Map document filename to page names
        self.page_map = {}
        for pagenode in root.find('namespace').iter('page'):
            if pagenode.get('subtype') not in ('page', 'example', 'internal') and not self.options.get('force_pages', False):
                if self.verbosity >= 2:
                    print "%s page type: %s" % (pagenode.get('href'), pagenode.get('subtype'))
                continue
            pagename = self.parse_pagename(pagenode.get('name'))
            ns_name = self.parse_namespace(pagenode.get('module'))
            if ns_name is not None:
               self.page_map[pagenode.get('href')] = ns_name+'.'+pagename
            else:
                self.page_map[pagenode.get('href')] = pagename

            if self.options.get('all_pages'):
                self.page_refs[pagenode.get('href')] = 1

        # Import QML class documentation
        for qmlclass in root.find('namespace').iter(class_node):
            if qmlclass.get('status') == 'obsolete':
                print "Warning: Skipping obsolete class: %s" % qmlclass.get('name')
                continue

            classname = self.parse_classname(qmlclass.get('name'))
            ns_name = self.parse_namespace(qmlclass.get(class_module, None))
            self.import_class(qmlclass.get('href'), classname, ns_name)
            
        page_order_index = 0
        #if os.path.exists(os.path.join(self.DOC_ROOT, 'index.html')) and 'index.html' not in self.page_refs and 'index.html' not in self.class_map:
        #    self.import_page('index.html', 'index', root.get('title'), self.parse_namespace(self.PRIMARY_NAMESPACE), 0)
        #    page_order_index = 1

        while 1 in self.page_refs.values():
            if self.verbosity >= 2:
                print "Page refs needing import: %s'" % self.page_refs.keys()
            for pagenode in root.find('namespace').iter('page'):
                # Only import pages that are referenced elsewhere
                if pagenode.get('href') not in self.page_refs:
                    continue
                
                # Only import pages with pending references
                if self.page_refs[pagenode.get('href')] == 0:
                    continue
    
                # Remove this page from the reference list so it won't be imported again
                self.page_refs[pagenode.get('href')] = 0
                
                try:
                    self.import_page(pagenode.get('href'), pagenode.get('href'), pagenode.get('title'), self.parse_namespace(pagenode.get('module')), page_order_index)
                    page_order_index += 1
                except Exception as e:
                    print "Failed to import page '%s''" % (pagenode.get('href'))
                    import pdb; pdb.set_trace()
                    self.import_page(pagenode.get('href'), pagenode.get('href'), pagenode.get('title'), self.parse_namespace(pagenode.get('module')), page_order_index)
                    

    def import_class(self, classhref, classname, ns_name):
        doc_file = os.path.join(self.DOC_ROOT, classhref)
        if not os.path.exists(doc_file):
            print "Warning: Could not find QML class %s doc file %s, skipping" % (classname, classhref)
            return
            
        if ns_name is not None:
            namespace, created = Namespace.objects.get_or_create(name=ns_name, platform_section=self.section)
        else:
            namespace = None

        if namespace is not None:
            fullname = namespace.name + '.' + classname
        else:
            fullname = classname
        element, created = Element.objects.get_or_create(name=classname, fullname=fullname, section=self.section, namespace=namespace)
            
        if self.verbosity >= 1:
            print 'Element: ' + element.fullname
            
        doc_handle = open(doc_file)
        doc_data = doc_handle.readlines()
        doc_handle.close()
        
        doc_start = 2
        doc_end = -2
        for i, line in enumerate(doc_data):
            if '<h1 class="title"' in line:
                doc_start = i+1
            if '<div class="footer"' in line:
                doc_end = i-1
            elif '<footer' in line:
                doc_end = i-1
        if self.verbosity >= 3:
            print "Doc range: %s:%s" % (doc_start, doc_end)

        try:
            brief_start = doc_data.index('<!-- $$$'+element.name+'-brief -->\n')
            element.description = self.strip_links(doc_data[brief_start+1][3:-35])
            if len(element.description) >= 256:
                element.description = element.description[:252]+'...'
        except ValueError:
            pass

        try:
            # Change the content of the docs 
            cleaned_data = ''
            for line in doc_data[doc_start:doc_end]:
                if line == '' or line == '\n':
                    continue
                if 'List of all members, including inherited members' in line:
                    continue
                line = self.parse_line(line, classhref, fullname)
                if isinstance(line, unicode):
                    line = line.encode('ascii', 'replace')
                cleaned_data += line
                
            element.data = cleaned_data
        except Exception, e:
            print "Parsing content failed:"
            print e
            #import pdb; pdb.set_trace()
            
        element.source_file = os.path.basename(doc_file)
        element.source_format = "qdoc"
        element.save()

        
    def import_page(self, pagehref, pagename, pagetitle, ns_name, page_order_index):
        if pagename.endswith('.html'):
            pagename = pagename[:-5]

        doc_file = os.path.join(self.DOC_ROOT, pagehref)
        if not os.path.exists(doc_file):
            print "Warning: Could not find QML page %s doc file %s, skipping" % (pagename, pagehref)
            return

        if ns_name is not None:
            namespace, created = Namespace.objects.get_or_create(name=ns_name, platform_section=self.section)
        else:
            namespace = None
            
        if namespace is not None:
            if pagename == ns_name:
                fullname = 'index'
            else:
                fullname = namespace.name + '.' + pagename
        else:
            fullname = pagename
            
        if not pagetitle:
            pagetitle = pagename

        if len(pagetitle) >= 64:
            pagetitle = pagetitle[:60]+'...'
        page, created = Page.objects.get_or_create(slug=pagename, fullname=fullname, title=pagetitle, section=self.section, namespace=namespace)

        if self.verbosity >= 1:
            print 'Page[%s]: %s' % (page_order_index, page.slug)
        
        doc_handle = open(doc_file)
        doc_data = doc_handle.readlines()
        doc_handle.close()
        
        doc_start = 2
        doc_end = -2
        for i, line in enumerate(doc_data):
            if '<body' in line:
                doc_start = i+1
            elif '<h1 class="title">' in line:
                doc_start = i+1
            if '<div class="footer"' in line:
                doc_end = i-1
            elif '<footer' in line:
                doc_end = i-1
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
                line = self.parse_line(line, pagehref, pagename)
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
        page.source_format = "qdoc"
        page.order_index = page_order_index
        page.save()

