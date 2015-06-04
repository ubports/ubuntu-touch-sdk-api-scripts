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
        self.pages_sections = dict()
        self.page_data_map = dict()
        self.module_order = []

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
        if anchor is None:
            anchor = ''
        
        if anchor != '' and anchor[1:] in self.class_map:
            return anchor[1:]
            
        rel_url = os.path.relpath(os.path.join(element_fullname, url))
        if rel_url in self.class_map or rel_url in self.page_map:
            return rel_url
        
        url_part = url.replace('../', '')
        if url_part.endswith('/'):
            url_part = url_part[:-1]
            
        if url_part in self.class_map or url_part in self.page_map:
            return url_part
            
        anchor_part = anchor[1:anchor.rfind('.')]
        if anchor_part in self.class_map or anchor_part in self.page_map:
            return anchor_part
            
        anchor_with_ns = element_fullname[:element_fullname.rfind('.')] + '.'+anchor[1:]
        if anchor_with_ns in self.class_map or anchor_with_ns in self.page_map:
            return anchor_with_ns
            
        anchor_without_function = anchor_with_ns[:anchor_with_ns.rfind('.')]
        if anchor_without_function in self.class_map or anchor_without_function in self.page_map:
            return anchor_without_function
            
        return url

    def get_section(self, namespace, fullname):
        if fullname is not None and fullname in SECTIONS:
            return SECTIONS[fullname]
        elif namespace is not None and namespace in SECTIONS:
            return SECTIONS[namespace]
        elif fullname is not None and '/' in fullname and fullname.split('/')[0]+'/' in SECTIONS:
            return SECTIONS[fullname.split('/')[0]+'/']
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
        if self.verbosity >= 2:
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
                if "<span class=\"viewcode-link\">[source]</span>" in line:
                    line = line.replace("<span class=\"viewcode-link\">[source]</span>", "")
                if '<div class="section" id="' in line:
                    start_div = line.find('<div class="section"')
                    end_div = line.find('>', start_div)
                    line = line[:start_div] + line[end_div+1:]
                if '<h1><tt class="docutils literal"><span class="pre">' in line:
                    start_div = line.find('<h1><tt class="docutils literal"><span class="pre">')
                    end_div = line.find('</h1>', start_div)
                    line = line[:start_div] + line[end_div+5:]
                line = self.parse_line(line, doc_file, element_fullname)
                cleaned_data += line + '\n'
                
            return cleaned_data
        except Exception, e:
            print "Parsing content failed: "
            import pdb; pdb.set_trace()
            print e
            return unclean_data
                
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

        module_order_index = 0
            
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
            if self.verbosity >= 3:
                print "Object: %s" % obj_item
            obj_data = obj_item.split(' ')
            try:
                fullname, doc_type, doc_enum, href = obj_data[0:4]
            except ValueError:
                print "Not enough values: %s" % obj_item
                exit(1)
            if doc_enum == DOC_MODULE:
                page_path, page_anchor = href.split('#')
                if page_path.endswith('/'):
                    page_path = page_path[:-1]
                ns_name = fullname
                self.module_order.append(fullname)
                self.namespace_map[fullname] = page_path
            elif doc_enum == DOC_API_PART:
                ns_name = '.'.join(fullname.split('.')[:2])
                if doc_type == 'py:class':
                    self.class_map[fullname] = fullname
                elif doc_type == 'py:method':
                    self.class_map[fullname] = '.'.join(fullname.split('.')[:-1])
            elif doc_enum == DOC_PAGE:
                if self.verbosity >= 2:
                    print "Found Page: %s" % fullname
                ns_name = ''
                page_path, page_anchor = href.split('#')
                if page_path.endswith('/'):
                    page_path = page_path[:-1]

                if page_anchor == '#$':
                    page_anchor = '#'+fullname

                if self.verbosity >= 2:
                    print "Adding Page: %s" % page_path
                if len(obj_data) > 4:
                    page_title = ' '.join(obj_data[4:])
                else:
                    page_title = page_anchor

                if page_path not in self.pages_sections:
                    self.pages_sections[page_path] = dict()
                self.pages_sections[page_path][page_anchor] = fullname

                if not page_path in self.page_order:
                    self.page_map[page_path] = self.parse_pagename(page_path)
                    self.page_data_map[page_path] = (ns_name, fullname, fullname, page_title)
                    self.page_order.append(page_path)
            else:
                ns_name = ''
                
            continue
            
        for module in self.module_order:

            doc_file = os.path.join(self.DOC_ROOT, self.namespace_map[module]+'.fjson')
            module_data = self.read_json_file(doc_file)
            classes, extra = self.extract_classes(module_data['body'])

            if len(classes) > 0:
                            
                for fullname, doc_data in classes:
                    if '.' in fullname:
                        ns_name = fullname[:fullname.rindex('.')]
                        classname = fullname[fullname.rindex('.')+1:]
                    else:
                        classname = fullname
                        ns_name = None

                    cleaned_ns_name = self.parse_namespace(ns_name)

                    section, created = Section.objects.get_or_create(name=self.get_section(ns_name, None), topic_version=self.version)
                    if created:
                        print "Created section: %s" % section.name

                    if self.verbosity >= 1:
                        print 'Namespace: ' + ns_name
                        print 'Section: ' + section.name

                    if cleaned_ns_name is not None and cleaned_ns_name != '':
                        namespace, created = Namespace.objects.get_or_create(name=ns_name, display_name=cleaned_ns_name, platform_section=section)
                        if created:
                            print "Created Namespace: %s" % ns_name
                        namespace.data = self.clean_content(extra, doc_file, ns_name)
                        namespace.source_file = os.path.basename(doc_file)
                        namespace.source_format = "sphinx"
                        namespace.save()
                    else:
                        namespace = None
                        

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
                
        #exit(0)
        
        if not self.options.get('no_pages', False):
            page_order_index = 0
            
            #self.page_order.extend(self.module_order)
                
            for pagefile in self.pages_sections:
                ns_name, pagename, pagefullname, pagetitle = self.page_data_map[pagefile]
                try:
                    self.import_page(pagefile, ns_name, page_order_index)
                    page_order_index += 1
                except Exception as e:
                    print "Failed to import page '%s': %s'" % (pagefile, e)

    def import_page(self, pagehref, ns_name, page_order_index):
            doc_file = os.path.join(self.DOC_ROOT, pagehref+'.fjson')
            doc_data = self.read_json_file(doc_file)
            if not 'body' in doc_data:
                return
            doc_data = doc_data['body'].split('\n')

            cleaned_ns_name = self.parse_namespace(ns_name)
            section, section_created = Section.objects.get_or_create(name=self.get_section(ns_name, pagehref), topic_version=self.version)
            if section_created:
                print "Created section: %s" % section.name
            
            if cleaned_ns_name is not None and cleaned_ns_name != '':
                namespace, created = Namespace.objects.get_or_create(name=ns_name, display_name=cleaned_ns_name, platform_section=section)
            else:
                namespace = None

            pagename = self.parse_pagename(pagehref)
            page, created = Page.objects.get_or_create(slug=pagename, fullname=pagename, section=section, namespace=namespace)
            if not page.title:
                page.title = pagename
                page.save()
            
            doc_start = 2
            doc_end = len(doc_data)
            for i, line in enumerate(doc_data):
                if '<h1>' in line:
                    page.title = self.just_text(line[line.find('<h1>')+4:line.find('</h1>', 4)])
                    if len(page.title) >= 64:
                        page.title = page.title[:60]+'...'
                    if self.verbosity >= 2:
                        print "Setting title of %s to: %s" % (pagename, page.title)
                    page.save()

            try:
                # Change the content of the docs 
                cleaned_data = ''
                for line in doc_data[doc_start:doc_end]:
                    line = self.parse_line(line, pagehref, pagehref)
                    if isinstance(line, unicode):
                        line = line.encode('ascii', 'replace')
                    cleaned_data += line + '\n'
                    
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
                    if '<h1 class="title">' in line:
                        continue
                    line = self.parse_line(line, nshref, nsfullname)
                    if isinstance(line, unicode):
                        line = line.encode('ascii', 'replace')
                    cleaned_data += line + '\n'
                    
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
