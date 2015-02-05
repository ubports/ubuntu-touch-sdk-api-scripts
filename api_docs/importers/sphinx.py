# Import DQoc HTML from lp:ubuntu-ui-toolkit
import os, sys, re

import zlib
import simplejson

from django.core.files import File
from django.core.files.storage import get_storage_class

from ..models import *
from . import Importer


__all__ = (
    'SphinxImporter',
)

SECTIONS = dict()

class SphinxImporter(Importer):

    SOURCE_FORMAT = "sphinx"
    
    def __init__(self, *args, **kwargs):
        super(SphinxImporter, self).__init__(*args, **kwargs)
        self.source = self.options.get('dir')
        self.DOC_ROOT = self.source
        self.sections_file = self.options.get('sections')

    def parse_line(self, line, source_file, element_fullname):
        line = line.replace(u'\u00b6', u'')
        return super(SphinxImporter, self).parse_line(line, source_file, element_fullname)
        
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

    def lookup_from_url(self, url, anchor, element_fullname):
        if not anchor:
            return url
        
        if anchor != '' and anchor[1:] in self.class_map:
            return anchor[1:]
            
        anchor_part = anchor[1:anchor.rfind('.')]
        if anchor_part in self.class_map:
            return anchor_part
            
        anchor_with_ns = element_fullname[:element_fullname.rfind('.')] + '.'+anchor[1:]
        if anchor_with_ns in self.class_map:
            return anchor_with_ns
            
        anchor_without_function = anchor_with_ns[:anchor_with_ns.rfind('.')]
        if anchor_without_function in self.class_map:
            return anchor_without_function
            
        return url

    def get_section(self, namespace, fullname):
        if fullname in SECTIONS:
            return SECTIONS[fullname]
        elif namespace in SECTIONS:
            return SECTIONS[namespace]
        else:
            return SECTIONS["*"]
    
    def read_inv_file(self, filepath):
        inv_file = open(filepath)
        inv_file_data = inv_file.readlines()
        inv_compressed_data = ''.join(inv_file_data[4:])
        try:
            inv_data = zlib.decompress(inv_compressed_data)
            return inv_data.split('\n')
        except Exception, e:
            print "Error reading inv:\n%s" % filepath
            raise e
        
    def read_json_file(self, filepath):
        js_file = open(filepath)
        js_data = js_file.read()
        try:
            json_object = simplejson.loads(js_data)
            return json_object
        except Exception, e:
            print "Error parsing JSON:\n%s" % js_data
            raise e

    def extract_classes(self, module_html):
        classes = []
        current_class = None
        current_class_start = 0
        extra_end = len(module_html)
        i = 0
        if isinstance(module_html, (str,unicode)) and '\n' in module_html:
            module_html = module_html.split('\n')
        html_len = len(module_html)
        if self.verbosity >= 1:
            print "Looking for classes in %s lines" % html_len

        while i < html_len:
            line = module_html[i]
            if line == "<dl class=\"class\">":
                if i <= extra_end:
                    extra_end = i-0
                if current_class:
                    classes.append((current_class, module_html[current_class_start:i]))
                    if self.verbosity >= 1:
                        print "Found class: %s" % current_class
                current_class_start = i
                # <dt id="autopilot.process.ProcessManager">
                current_class = module_html[i+1][8:-2]
            i += 1
        if current_class:
            classes.append((current_class, module_html[current_class_start:-1]))
            if self.verbosity >= 1:
                print "Found class: %s" % current_class
        return classes, module_html[1:extra_end]
            
    def clean_content(self, unclean_data, doc_file, element_fullname):
        if unclean_data is None:
            return None
        try:
            # Change the content of the docs 
            cleaned_data = ''
            for line in unclean_data:
                if line == '' or line == '\n':
                    continue
                if "<span class=\"viewcode-link\">[source]</span>" in line:
                    line = line.replace("<span class=\"viewcode-link\">[source]</span>", "")
                if '<div class="section" id="quick-start">' in line:
                    line = line.replace('<div class="section" id="quick-start">', "")
                line = self.parse_line(line, doc_file, element_fullname)
                cleaned_data += line
                
            return cleaned_data
        except Exception, e:
            print "Parsing content failed: "
            import pdb; pdb.set_trace()
            print e
            return unclean_data
        
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
                        self.page_map[namespace_file] = (namespace_parent, namespace_shortname, namespace_fullname, namespace_fullname)
                        self.namespace_order.append(namespace_file)
                    if isinstance(namespace_data, (str, unicode)) and os.path.exists(os.path.join(self.source, namespace_data+'.js')):
                        child_data = self.read_json_file(os.path.join(self.source, namespace_data+'.js'))
                        self.read_classes(child_data, namespace_fullname)
                elif namespace_file.startswith('class'):
                    print "Class: %s" % (namespace_fullname)
                    if namespace_file not in self.class_map:
                        self.class_map[namespace_file] = (namespace_parent, namespace_shortname, namespace_fullname)
                    if isinstance(namespace_data, (str, unicode)) and os.path.exists(os.path.join(self.source, namespace_data+'.js')):
                        child_data = self.read_json_file(os.path.join(self.source, namespace_data+'.js'))
                        self.read_classes(child_data, namespace_fullname)
                elif namespace_file.startswith('struct'):
                    print "Struct: %s" % (namespace_fullname)
                    if namespace_file not in self.class_map:
                        self.class_map[namespace_file] = (namespace_parent, namespace_shortname, namespace_fullname)

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
                    self.page_map[page_file] = (namespace_parent, page_shortname, page_fullname, page_title)
                    self.page_order.append(page_file)

                if page_data:
                    if isinstance(page_data, list):
                        self.read_pages(page_data, namespace_parent)
        
    def run(self):
        self.source = self.options.get('inv')
        if not os.path.exists(self.source):
            print "Source directory not found"
            exit(1)
            
        self.sections_file = self.options.get('sections')
        if not self.sections_file:
            print "You must define a sections definition file to import Sphinx API docs"
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
                
        objects = self.read_inv_file(self.source)
        
        self.DOC_ROOT = os.path.dirname(self.source)
        
        self.PRIMARY_NAMESPACE = None

        namespace_order_index = 0
            
        DOC_MODULE = '0'
        DOC_API_PART = '1'
        DOC_PAGE = '-1'
        
        self.inventory = {
            'namespaces': [],
            'classes': [],
            'pages': [],
        }
        # Import class documentation
        for obj_item in objects:
            if not obj_item:
                continue
            #autopilot.display py:module 0 api/autopilot.display/#module-$ -
            obj_data = obj_item.split(' ')
            try:
                fullname, doc_type, doc_enum, href = obj_data[0:4]
            except ValueError:
                print "Not enough values: %s" % obj_item
                exit(1)
            if doc_enum == DOC_MODULE:
                ns_name = fullname
                self.namespace_order.append(fullname)
            elif doc_enum == DOC_API_PART:
                ns_name = '.'.join(fullname.split('.')[:2])
                if doc_type == 'py:class':
                    self.class_map[fullname] = fullname
                elif doc_type == 'py:method':
                    self.class_map[fullname] = '.'.join(fullname.split('.')[:-1])
            elif doc_enum == DOC_PAGE:
                ns_name = ''
                self.page_map[fullname] = fullname
            else:
                ns_name = ''
                
            
            print "Namespace: %s" % ns_name
            print "API part: %s" % fullname
            continue
            
        for ns_name in self.namespace_order:
            cleaned_ns_name = self.parse_namespace(ns_name)

            section, created = Section.objects.get_or_create(name=self.get_section(ns_name, None), topic_version=self.version)

            if self.verbosity >= 1:
                print 'Namespace: ' + ns_name
                print 'Section: ' + section.name

                
            doc_file = os.path.join(self.DOC_ROOT, 'api', ns_name+'.fjson')
            ns_data = self.read_json_file(doc_file)
            classes, extra = self.extract_classes(ns_data['body'])

            if cleaned_ns_name is not None and cleaned_ns_name != '':
                namespace, created = Namespace.objects.get_or_create(name=ns_name, display_name=cleaned_ns_name, platform_section=section)
                if created:
                    print "Created Namespace: %s" % ns_name
                namespace.data = self.clean_content(extra, doc_file, ns_name)
                namespace.save()
            else:
                namespace = None

            if len(classes) > 0:
                            
                for fullname, doc_data in classes:
                    if fullname.startswith(ns_name):
                        classname = fullname[len(ns_name)+1:]
                    else:
                        classname = fullname

                    if self.verbosity >= 1:
                        print 'Element: ' + fullname

                    element, created = Element.objects.get_or_create(name=classname, fullname=fullname, section=section, namespace=namespace)
                        
                                        
                    try:
                        for line in doc_data:
                            if line.startswith('<dd><p>'):
                                desc_line = self.parse_line(line[7:-4], doc_file, fullname)
                                link_replacer = re.compile('<a [^>]*>([^<]+)</a>')
                                while link_replacer.search(desc_line):
                                    desc_line = link_replacer.sub('\g<1>', desc_line, count=1)
                                if len(desc_line) >= 256:
                                    desc_line = desc_line[:252]+'...'
                                element.description = desc_line
                                break
                    except ValueError:
                        pass

                    element.data = self.clean_content(doc_data, doc_file, fullname)
                    element.source_file = os.path.basename(doc_file)
                    element.source_format = "sphinx"
                    element.save()
                
        exit(0)
        
        if not self.options.get('no_pages', False):
            page_order_index = 0
            
            self.page_order.extend(self.namespace_order)
                
            for pagefile in self.page_order:
                ns_name, pagename, pagefullname, pagetitle = self.page_map[pagefile]
                if pagename == 'notitle':
                    pagename = 'index'
                    pagefullname = 'index'
                    pagetitle = 'Introduction'
                try:
                    self.import_page(pagefile, pagename, pagetitle, pagefullname, ns_name, page_order_index)
                    page_order_index += 1
                except ServiceOperationFailed as e:
                    print "Failed to import page '%s': %s'" % (pagefile, e.message)

    def import_page(self, pagehref, pagename, pagetitle, pagefullname, ns_name, page_order_index):
            if pagename.endswith('.html'):
                pagename = pagename[:-5]

            cleaned_ns_name = self.parse_namespace(ns_name)
            section = Section.objects.get(name=self.get_section(ns_name, pagename), topic_version=self.version)
            
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
            page.source_format = "sphinx"
            page.order_index = page_order_index
            page.save()

    def import_namespace(self, nshref, nsname, nstitle, nsfullname, parent_ns_name, ns_order_index):
            if nsname.endswith('.html'):
                nsname = nsname[:-5]

            section = Section.objects.get(name=self.get_section(nsname, None), topic_version=self.version)
            
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
            ns.source_format = "sphinx"
            ns.order_index = ns_order_index
            ns.save()
