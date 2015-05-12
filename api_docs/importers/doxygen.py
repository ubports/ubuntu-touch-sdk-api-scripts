# Import DQoc HTML from lp:ubuntu-ui-toolkit
import os, sys, re

import simplejson

from django.core.files import File
from django.core.files.storage import get_storage_class

from ..models import *
from . import Importer


__all__ = (
    'DoxygenImporter',
)

SECTIONS = {}

class DoxygenImporter(Importer):

    SOURCE_FORMAT = "qdoc"
    
    def __init__(self, *args, **kwargs):
        super(DoxygenImporter, self).__init__(*args, **kwargs)
        self.source = self.options.get('dir')
        self.DOC_ROOT = self.source
        self.sections_file = self.options.get('sections')
        self.class_data_map = {}
        self.page_data_map = {}

    def parse_pagename(self, pagename):
        if pagename.endswith('.html'):
            pagename = pagename[:-5]
        return pagename.replace('/', '-').replace(' ', '_')

    def parse_namespace(self, namespace):
        if self.options.get('strip_namespace', None) and namespace:
            strip_prefix = self.options.get('strip_namespace')
            if namespace.startswith(strip_prefix):
                namespace = namespace[len(strip_prefix):]
            elif strip_prefix.startswith(namespace):
                namespace = ''
                
            if namespace.startswith('.'):
                namespace = namespace[1:]

        if self.options.get('namespace', None) and not namespace:
            return self.options.get('namespace')

        return namespace

    def get_section(self, namespace, fullname):
        if fullname in SECTIONS:
            return SECTIONS[fullname]
        elif namespace in SECTIONS:
            return SECTIONS[namespace]
        else:
            return SECTIONS['*']
    
    def read_json_file(self, filepath):
        js_file = open(filepath)
        js_data = js_file.readlines()
        js_file.close()
        try:
            endvar = js_data.index("];\n")+1
        except ValueError:
            endvar = len(js_data)
        try:
            json_data = ''.join(js_data[1:endvar]).replace('\n', '').replace("'", '"').replace(';', '')
            json_object = simplejson.loads(json_data)
            return json_object
        except Exception as e:
            import pdb; pdb.set_trace()
            return ''
        
    def run(self):

        if not os.path.exists(self.source):
            print "Source directory not found"
            exit(1)
            
        if not self.sections_file:
            print "You must define a sections definition file to import Doxygen API docs"
            exit(2)
        elif not os.path.exists(self.sections_file):
            print "Sections definition file not found"
            exit(1)
        else:
            sections_file_dir = os.path.dirname(self.sections_file)
            if sections_file_dir:
                if self.verbosity >= 2:
                    print "Adding to PYTHONPATH: %s" % sections_file_dir
                sys.path.append(sections_file_dir)
            sections_file_module = os.path.basename(self.sections_file)
            if sections_file_module.endswith('.py'):
                sections_file_module = sections_file_module[:-3]
            if self.verbosity >= 2:
                print "Importing module: %s" % sections_file_module
            sections_data = __import__(sections_file_module)
            
            if hasattr(sections_data, 'SECTIONS') and isinstance(sections_data.SECTIONS, dict):
                SECTIONS.update(sections_data.SECTIONS)
            else:
                print "Sections file does not contain a SECTIONS dictionary"
                exit(3)
                
        self.read_classes(self.read_json_file(os.path.join(self.source, 'annotated.js')))
        if not self.options.get('no_pages', False):
            if os.path.exists(os.path.join(self.source, 'navtreedata.js')):
                self.read_pages(self.read_json_file(os.path.join(self.source, 'navtreedata.js')), self.parse_namespace(None))
            elif os.path.exists(os.path.join(self.source, 'navtree.js')):
                self.read_pages(self.read_json_file(os.path.join(self.source, 'navtree.js')), self.parse_namespace(None))
        #exit(0)
            
        namespace_order_index = 0
            
        #print "Namespace_order: %s" % self.namespace_order
        #for nsfile in self.namespace_order:
            #parent_ns_name, nsname, nsfullname, nstitle = self.namespace_map[nsfile]
            #try:
                #self.import_namespace(nsfile, nsname, nstitle, nsfullname, parent_ns_name, namespace_order_index)
                #namespace_order_index += 1
            #except ServiceOperationFailed as e:
                #print "Failed to import namespace '%s': %s'" % (nsfile, e.message)


        # Import class documentation
        for classfile, classdef in self.class_data_map.items():
            ns_name, classname, fullname = classdef
            cleaned_ns_name = self.parse_namespace(ns_name)

            section, section_created = Section.objects.get_or_create(name=self.get_section(ns_name, fullname), topic_version=self.version)

            if cleaned_ns_name is not None and cleaned_ns_name != '':
                namespace, created = Namespace.objects.get_or_create(name=ns_name, display_name=cleaned_ns_name, platform_section=section)
                if created:
                    print "Created Namespace: %s" % ns_name
            else:
                namespace = None

            element, created = Element.objects.get_or_create(name=classname, fullname=fullname, section=section, namespace=namespace)
                
            if self.verbosity >= 1:
                print 'Element: ' + element.fullname
                
            doc_file = os.path.join(self.DOC_ROOT, classfile)
            doc_handle = open(doc_file)
            doc_data = doc_handle.readlines()
            doc_handle.close()
            
            doc_start = 2
            doc_end = len(doc_data)
            for i, line in enumerate(doc_data):
                if '<div class="contents">' in line:
                    doc_start = i+1
                if '</div><!-- contents -->' in line and doc_end > i:
                    doc_end = i-1
                if '<hr/>The documentation for this ' in line and ' was generated from the following' in line and doc_end > i:
                    doc_end = i-1
            if self.verbosity >= 2:
                print "Doc range: %s:%s" % (doc_start, doc_end)

            try:
                brief_start = doc_data.index('<div class="contents">\n')
                desc_line = self.parse_line(doc_data[brief_start+2][3:], classfile, fullname)
                link_replacer = re.compile('<a [^>]*>([^<]+)</a>')
                while link_replacer.search(desc_line):
                    desc_line = link_replacer.sub('\g<1>', desc_line, count=1)
                if len(desc_line) >= 256:
                    desc_line = desc_line[:252]+'...'
                element.description = desc_line
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
                    line = self.parse_line(line, classfile, fullname)
                    if isinstance(line, unicode):
                        line = line.encode('ascii', 'replace')
                    cleaned_data += line
                    
                element.data = cleaned_data
            except Exception, e:
                print "Parsing content failed:"
                print e
                #import pdb; pdb.set_trace()
                
            element.source_file = os.path.basename(doc_file)
            element.source_format = "doxygen"
            element.save()
            
        if not self.options.get('no_pages', False):
            page_order_index = 0
            
            self.page_order.extend(self.namespace_order)
                
            for pagefile in self.page_order:
                ns_name, pagename, pagefullname, pagetitle = self.page_data_map[pagefile]
                if pagename == 'notitle':
                    pagename = 'index'
                    pagefullname = 'index'
                    pagetitle = 'Introduction'
                try:
                    self.import_page(pagefile, pagename, pagetitle, pagefullname, ns_name, page_order_index)
                    page_order_index += 1
                except ServiceOperationFailed as e:
                    print "Failed to import page '%s': %s'" % (pagefile, e.message)

    def read_classes(self, ns_data, namespace_parent=None):
        for namespace_def in ns_data:
            namespace_shortname = namespace_def[0]
            namespace_file = namespace_def[1]
            namespace_data = namespace_def[2]
            if namespace_parent:
                namespace_fullname = namespace_parent + '.' + namespace_shortname
            else:
                namespace_fullname = namespace_shortname

            if namespace_file and namespace_data:
                if '#' in namespace_file:
                    namespace_file = namespace_file[:namespace_file.index('#')]
                else:
                    namespace_file = namespace_file

                if namespace_file.startswith('namespace'):
                    print "Namespace: %s" % (namespace_fullname)
                    if namespace_file not in self.namespace_map:
                        self.page_map[namespace_file] = namespace_fullname
                        self.page_data_map[namespace_file] = (namespace_parent, namespace_shortname, namespace_fullname, namespace_fullname)
                        self.namespace_order.append(namespace_file)
                    if isinstance(namespace_data, (str, unicode)) and os.path.exists(os.path.join(self.source, namespace_data+'.js')):
                        child_data = self.read_json_file(os.path.join(self.source, namespace_data+'.js'))
                        self.read_classes(child_data, namespace_fullname)
                elif namespace_file.startswith('class'):
                    print "Class: %s" % (namespace_fullname)
                    if namespace_file not in self.class_map:
                        self.class_map[namespace_file] = namespace_fullname
                        self.class_data_map[namespace_file] = (namespace_parent, namespace_shortname, namespace_fullname)
                    if isinstance(namespace_data, (str, unicode)) and os.path.exists(os.path.join(self.source, namespace_data+'.js')):
                        child_data = self.read_json_file(os.path.join(self.source, namespace_data+'.js'))
                        self.read_classes(child_data, namespace_fullname)
                elif namespace_file.startswith('struct'):
                    print "Struct: %s" % (namespace_fullname)
                    if namespace_file not in self.class_map:
                        self.class_map[namespace_file] = namespace_fullname
                        self.class_data_map[namespace_file] = (namespace_parent, namespace_shortname, namespace_fullname)

            elif namespace_data:
                if isinstance(namespace_data, list):
                    self.read_classes(namespace_data, namespace_fullname)
                    
    def read_pages(self, ns_data, namespace_parent=None):
        for namespace_def in ns_data:
            page_title = namespace_def[0]
            page_href = namespace_def[1]
            page_data = namespace_def[2]
            
            if page_title in ("Namespaces", "Classes", "Files"):
                return
                
            if page_href == 'index.html' and self.options.get('no_index', False):
                return

            if page_href:
                if '#' in page_href:
                    page_file = page_href[:page_href.index('#')]
                else:
                    page_file = page_href
                    
                if page_file.endswith('.html'):
                    page_shortname = page_file[:-5]
                else:
                    page_shortname = page_file
                    
                if namespace_parent:
                    page_fullname = namespace_parent + '.' + page_shortname
                else:
                    page_fullname = page_shortname

                if not page_file in self.page_map:
                    print "Page: %s" % (page_file)
                    self.page_map[page_file] = page_fullname
                    self.page_data_map[page_file] = (namespace_parent, page_shortname, page_fullname, page_title)
                    self.page_order.append(page_file)

                if page_data:
                    if isinstance(page_data, list):
                        self.read_pages(page_data, namespace_parent)
        

    def import_page(self, pagehref, pagename, pagetitle, pagefullname, ns_name, page_order_index):
            if pagename.endswith('.html'):
                pagename = pagename[:-5]

            cleaned_ns_name = self.parse_namespace(ns_name)
            section, section_created = Section.objects.get_or_create(name=self.get_section(ns_name, pagename), topic_version=self.version)
            
            if cleaned_ns_name is not None and cleaned_ns_name != '':
                namespace, created = Namespace.objects.get_or_create(name=ns_name, display_name=cleaned_ns_name, platform_section=section)
            else:
                namespace = None
                                
            if len(pagetitle) >= 64:
                pagetitle = pagetitle[:60]+'...'
            page, created = Page.objects.get_or_create(slug=pagename, fullname=pagefullname, title=pagetitle, section=section, namespace=namespace)

            if self.verbosity >= 1:
                print 'Page[%s]: %s' % (page_order_index, page.slug)
            
            doc_file = os.path.join(self.DOC_ROOT, pagehref)
            doc_handle = open(doc_file)
            doc_data = doc_handle.readlines()
            doc_handle.close()
            
            doc_start = 2
            doc_end = len(doc_data)
            for i, line in enumerate(doc_data):
                if '<div class="contents">' in line:
                    doc_start = i+1
                if '</div><!-- doc-content -->' in line and doc_end > i:
                    doc_end = i-1
                if '<!-- start footer part -->' in line and doc_end > i:
                    doc_end = i-2
            if self.verbosity >= 2:
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
            page.source_format = "doxygen"
            page.order_index = page_order_index
            page.save()

    def import_namespace(self, nshref, nsname, nstitle, nsfullname, parent_ns_name, ns_order_index):
            if nsname.endswith('.html'):
                nsname = nsname[:-5]

            section, section_created = Section.objects.get_or_create(name=self.get_section(nsname, None), topic_version=self.version)
            
            if len(nstitle) >= 64:
                nstitle = nstitle[:60]+'...'
            ns, created = Namespace.objects.get_or_create(name=nsfullname, display_name=nsfullname, platform_section=section)

            if self.verbosity >= 1:
                print 'ns[%s]: %s' % (ns_order_index, ns.name)
            
            doc_file = os.path.join(self.DOC_ROOT, nshref)
            doc_handle = open(doc_file)
            doc_data = doc_handle.readlines()
            doc_handle.close()
            
            doc_start = 2
            doc_end = len(doc_data)
            for i, line in enumerate(doc_data):
                if '<div class="contents">' in line:
                    doc_start = i+1
                if '</div><!-- doc-content -->' in line and doc_end > i:
                    doc_end = i-1
                if '<!-- start footer part -->' in line and doc_end > i:
                    doc_end = i-2
            if self.verbosity >= 2:
                print "Doc range: %s:%s" % (doc_start, doc_end)

            try:
                # Change the content of the docs 
                cleaned_data = ''
                for line in doc_data[doc_start:doc_end]:
                    if line == '' or line == '\n':
                        continue
                    if '<h1 class="title">' in line:
                        continue
                    line = self.parse_line(line, nshref, nsfullname)
                    if isinstance(line, unicode):
                        line = line.encode('ascii', 'replace')
                    cleaned_data += line
                    
                ns.data = cleaned_data
            except Exception, e:
                print "Parsing content failed:"
                print e
                #continue
                #import pdb; pdb.set_trace()
            
            ns.source_file = os.path.basename(doc_file)
            ns.source_format = "doxygen"
            ns.order_index = ns_order_index
            ns.save()
