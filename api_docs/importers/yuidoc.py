# Import DQoc HTML from lp:ubuntu-ui-toolkit
import os

import simplejson

from django.core.files import File
from django.core.files.storage import get_storage_class

from ..models import *
from . import Importer


__all__ = (
    'YUIDocImporter',
)

class YUIDocImporter(Importer):

    SOURCE_FORMAT = "yuidoc"
    
    def __init__(self, *args, **kwargs):
        super(YUIDocImporter, self).__init__(*args, **kwargs)
        self.source = self.options.get('data')
        self.DOC_ROOT = os.path.dirname(self.source)
        self.in_foundat = False

    def parse_line(self, line, source_filename, element_fullname):
        if '<span class="foundat">' in line:
            if not '</span>' in line:
                self.in_foundat = True
            return ''
        if self.in_foundat:
            if '</span>' in line:
                self.in_foundat = False
                line.replace('</span>', '', 1)
            else:
                return ''
        clean_line = super(YUIDocImporter, self).parse_line(line, source_filename, element_fullname)
        clean_line = clean_line.replace('<a name="methods_', '<a name="')
        clean_line = clean_line.replace('<a name="props_', '<a name="')
        return clean_line
        
    def run(self):

        if not os.path.exists(self.source):
            print "Error: Source index file not found"
            exit(1)
            
        datafile = open(self.source)
        tree = simplejson.load(datafile)
        datafile.close()

        if 'modules' not in tree:
            print "Error: No <modules> section in %s" % self.source
            exit(2)
            
        tree_modules = tree.get('modules').values()
        if 'namespaces' in tree_modules[0] and len(tree_modules[0].get('namespaces')) > 0:
            self.PRIMARY_NAMESPACE = tree_modules[0].get('namespaces').keys()[0]
        else:
            self.PRIMARY_NAMESPACE = tree_modules[0].get('name')

        if 'classes' not in tree:
            print "Error No <classes> section in %s" % self.source
            exit(2)
            
        # Map document filenames to QML class names
        self.class_map = {}
        for jsclass in tree['classes'].values():
            classname = self.parse_classname(jsclass.get('name'))
            ns_name = self.parse_namespace(jsclass.get('module'))
            self.class_map['../classes/'+classname+'.html'] = ns_name + '.' + classname

        # Import YUI class documentation
        for jsclass in tree['classes'].values():
            ns_name = self.parse_namespace(jsclass.get('module'))
            classname = self.parse_classname(jsclass.get('name'))
            # Remove module name part of the classname
            if classname.startswith(ns_name+'.') and classname != ns_name:
                classname = classname[len(ns_name)+1:]

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
                
            element.description = jsclass.get('description').split('\n')[0]
            if len(element.description) >= 256:
                element.description = element.description[:252]+'...'

            doc_file = os.path.join(self.DOC_ROOT, 'classes', jsclass.get('name')+'.html')
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
                    line = self.parse_line(line, doc_file, fullname)
                    if isinstance(line, unicode):
                        line = line.encode('ascii', 'replace')
                    cleaned_data += line
                    
                element.data = cleaned_data
            except Exception, e:
                print "Parsing content failed:"
                print e
                #import pdb; pdb.set_trace()
                
            element.source_file = os.path.basename(doc_file)
            element.source_format = "yuidoc"
            element.save()

        page_order_index = 0
        if self.options.get('index', False) and os.path.exists(os.path.join(self.DOC_ROOT, 'index.html')):
            self.import_page('index.html', 'index', tree.get('project').get('name'), self.PRIMARY_NAMESPACE, page_order_index)
            page_order_index += 1
            
    def import_page(self, pagehref, pagename, pagetitle, ns_name, page_order_index):
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
            page.source_format = "yuidoc"
            page.order_index = page_order_index
            page.save()
            
