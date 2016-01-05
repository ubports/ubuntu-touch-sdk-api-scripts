import os, sys, re

from django.core.files import File
from django.core.files.storage import get_storage_class
from django.conf import settings

from api_docs.models import *

class Importer(object):

    def __init__(self, topic, language, version, section=None, options=dict()):
        self.topic = topic
        self.language = language
        self.version = version
        self.section = section

        self.options = options
        self.verbosity = int(options.get('verbosity', 1))
        
        self.PRIMARY_NAMESPACE = None
        self.DOC_ROOT = os.getcwd()
        
        self.class_map = {}
        self.page_map = {}
        self.page_refs = {}
        self.page_order = []
        self.namespace_map = {}
        self.namespace_order = []
        
        self.IMG_REGEX = re.compile(r'<img (?P<attribs>\w+=[\'"][\w\-\_\.\:\/\s]*[\'"]\s+)*src=[\'"](?P<url>[\w\-\_\.\:\/]*)(?P<anchor>#[\w\_\-\.]+)?[\'"][^>]*>')
        self.LINK_REGEX = re.compile(r'<a (?P<attribs>\w+=[\'"][\w\-\_\.\:\/\s]*[\'"]\s+)*href=[\'"](?P<url>[\w\-\_\.\:\/]*)(?P<anchor>#[\w\_\-\.]+)?[\'"][^>]*>(?P<text>.+)</a>')
                
        self.file_storage = get_storage_class()()
        
    def strip_links(self, line):
        clean_line = line
        removal = self.LINK_REGEX.search(line)
        while removal:
            source = removal.group(0)
            replace = removal.group('text')
            if '</a>' in replace:
                source = source[:source.index('</a>')+4]
                replace = replace[:replace.index('</a>')]
            if self.verbosity >= 3:
                print "Removing link: %s" % removal.group(0)
                print "  From: %s\n  To: %s" % (source, replace)
            clean_line = clean_line.replace(source, replace)
            removal = self.LINK_REGEX.search(clean_line)
        return clean_line

    def clean_links(self, line, source_filename, element_fullname=None):
        try:
            # Clean Links
            clean_line = line
            source_line = line
            #~ if source_filename in clean_line:
                #~ clean_line = clean_line.replace('href="'+source_filename+'#', 'href="#')
                #~ source_line = clean_line
                
            match = self.LINK_REGEX.search(source_line)
            while match:
                if self.verbosity >= 3:
                    print "Matched line [%s:%s]: %s " % (match.start(), match.end(), source_line)
                    
                match_url = match.group('url') or ''
                match_anchor = match.group('anchor') or ''
                if self.verbosity >= 2:
                    print "In: %s" % source_filename
                    print "  URL: %s" % match_url
                    print "  Anchor: %s" % match_anchor

                filename = self.lookup_from_url(match_url, match_anchor, element_fullname)

                if self.verbosity >= 2:
                    print "Checking for: %s" % filename
                    
                if filename in self.page_map:
                    if self.verbosity >= 2:
                        print "Found in page map: " + self.page_map[filename]
                    new_link = '/'.join(('/api', self.topic.slug, self.language.slug, self.version.slug, self.page_map[filename], ''))
                    clean_line = clean_line.replace('href="'+match_url+match_anchor, 'href="'+unicode.encode(new_link, 'ascii')+match_anchor)

                elif filename in self.class_map:
                    if self.verbosity >= 2:
                        print "Found in class map: " + self.class_map[filename]
                    new_link = '/'.join(('/api', self.topic.slug, self.language.slug, self.version.slug, self.class_map[filename], ''))
                    clean_line = clean_line.replace('href="'+match_url+match_anchor, 'href="'+unicode.encode(new_link, 'ascii')+match_anchor)

                # Replace links to things we don't recognize
                else:
                    if self.verbosity >= 2:
                        print "No direct link found, replacing them instead"
                    url_base = match.group('url').split('/')[-1]
                    if self.verbosity >= 2:
                        print "URL base: %s" % url_base
                    element = Element.objects.filter(source_file=url_base, source_format=self.SOURCE_FORMAT)
                    if element:
                        element = element[0]
                        new_link = '/'.join(('/api', element.section.topic_version.language.topic.slug, element.section.topic_version.language.slug, element.section.topic_version.slug, element.fullname, ''))
                        clean_line = clean_line.replace('href="'+match_url+match_anchor, 'href="'+unicode.encode(new_link, 'ascii')+match_anchor)
                    else:
                        page = Page.objects.filter(source_file=url_base, source_format=self.SOURCE_FORMAT)
                        if page:
                            page = page[0]
                            new_link = '/'.join(('/api', page.section.topic_version.language.topic.slug, page.section.topic_version.language.slug, page.section.topic_version.slug, page.fullname, ''))
                            clean_line = clean_line.replace('href="'+match_url+match_anchor, 'href="'+unicode.encode(new_link, 'ascii')+match_anchor)
                        # Remove links we couldn't match
                        elif '://' not in match.group('url'):
                            #if '://' in match.group('url'):
                                ## Continue trying to match on this line
                                #source_line = source_line[match.end():]
                                #match = self.LINK_REGEX.search(source_line)
                                #continue
                            if self.verbosity >= 3:
                                print "Removing links from: %s" % clean_line

                            removal = self.LINK_REGEX.search(clean_line)
                            while removal:
                                source = removal.group(0)
                                replace = removal.group('text')
                                if '</a>' in replace:
                                    source = source[:source.index('</a>')+4]
                                    replace = replace[:replace.index('</a>')]
                                if self.verbosity >= 3:
                                    print "Removing link: %s" % removal.group(0)
                                    print "  From: %s\n  To: %s" % (source, replace)
                                clean_line = clean_line.replace(source, replace)
                                removal = self.LINK_REGEX.search(clean_line)

                # Continue trying to match on this line
                source_line = source_line[match.end('url'):]
                match = self.LINK_REGEX.search(source_line)
            
            return clean_line
        except Exception, e:
            print "Error cleaning links: %s" % line
            if self.verbosity >= 2:
                import pdb; pdb.set_trace()
                self.parse_line(line, source_filename, element_fullname)
            elif self.verbosity >= 2:
                raise e
            else:
                return line

    def clean_images(self, line, source_filename, element_fullname=None):
        try:
            # Clean images
            clean_line = line
            source_line = line
            if '<img ' in line:
                img_match = self.IMG_REGEX.search(source_line)
                while img_match:
                    if self.verbosity >= 2:
                        print "Image in %s: %s" % (source_filename, img_match.group('url'))
                    if img_match.group('url').startswith('.'):
                        if source_filename.startswith('/'):
                            src_filename = os.path.abspath(os.path.join(os.path.dirname(source_filename), img_match.group('url')))
                            rel_filename = os.path.join('api', self.topic.slug, self.language.slug, self.version.slug, element_fullname, src_filename[len(self.DOC_ROOT)+1:])
                        else:
                            src_filename = os.path.abspath(os.path.join(self.DOC_ROOT, os.path.dirname(source_filename), img_match.group('url')))
                            rel_filename = os.path.join('api', self.topic.slug, self.language.slug, self.version.slug, element_fullname, src_filename[len(self.DOC_ROOT)+1:])
                    else:
                        src_filename = os.path.join(self.DOC_ROOT, img_match.group('url'))
                        rel_filename = os.path.join('api', self.topic.slug, self.language.slug, self.version.slug, element_fullname, img_match.group('url'))
                    if self.verbosity >= 2:
                        print "Uploading %s to %s" % (src_filename, rel_filename)
                    uploaded_file = self.upload_file(src_filename, rel_filename)
                    if self.verbosity >= 2:
                        print "Upload successful: %s" % uploaded_file
                    clean_line = clean_line.replace(img_match.group('url'), uploaded_file)
                    source_line = source_line[img_match.end():]
                    img_match = self.IMG_REGEX.search(source_line)
            return clean_line
        except Exception, e:
            print "Error cleaning images: %s" % line
            if self.verbosity >= 2:
                import pdb; pdb.set_trace()
                self.parse_line(line, source_filename, element_fullname)
            elif self.verbosity >= 2:
                raise e
            else:
                return line

    def just_text(self, line):
        while '<' in line:
            start_of_tag = line.find('<')
            end_of_tag = line.find('>', start_of_tag)
            line = line[:start_of_tag] + line[end_of_tag+1:]
        return line.encode('ascii', 'ignore')
        
    def parse_line(self, line, source_filename, element_fullname=None):
        clean_line = self.clean_images(line, source_filename, element_fullname)
        clean_line = self.clean_links(clean_line, source_filename, element_fullname)
        return clean_line

    def lookup_from_url(self, url, anchor, element_fullname):
        if not anchor:
            return url
        
        if anchor != '' and anchor[1:] in self.class_map:
            return anchor[1:]
        else:
            return url
        
    def parse_filename(self, filename):
        return filename
        
    def parse_href(self, href):
        return href
        
    def parse_pagename(self, pagename):
        if pagename.endswith('.html'):
            pagename = pagename[:-5]
        return pagename.replace('/', '-').replace(' ', '_')
        
    def parse_classname(self, classname):
        return classname
        
    def parse_namespace(self, namespace):
        if self.options.get('force_namespace', None):
            return self.options.get('force_namespace')
        elif self.options.get('namespace', None) and not namespace:
            return self.options.get('namespace')
        else:
            return namespace

    def upload_file(self, src_filename, rel_filename):
        if self.file_storage.exists(rel_filename):
            self.file_storage.delete(rel_filename)
        src_file = File(open(src_filename, 'rb'))
        dst_file = self.file_storage.save(rel_filename, src_file)
        src_file.close()
        return self.file_storage.url(dst_file)
 
    def run(self):
        raise NotImplementedError("Importer classes must define a 'run' method")
