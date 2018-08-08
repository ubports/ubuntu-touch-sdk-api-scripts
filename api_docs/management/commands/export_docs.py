#!/usr/bin/python
import os
import shutil
import re
import pypandoc

from django.core.management.base import BaseCommand

from api_docs.models import Page, Element, Language, Namespace


class Command(BaseCommand):
    help = "Export the docs as rst"

    BASE_DIR = '/tmp/sdk'
    # These are duplicates which should not be added to root toctrees
    DUPLICATES = ['actuator', 'hapticseffect', 'themeeffect']

    def paths(self, page):
        directory = '{}/{}/{}'.format(
            self.BASE_DIR,
            page.section.topic_version.language.topic.name,
            page.section.topic_version.language.name
        )

        title = page.title if type(page) == Page else page.name
        link = title
        path = '{}/{}'.format(directory, title).replace('/tmp/', '')
        if page.namespace:
            directory = '{}/{}'.format(directory, page.namespace.name)
            link = '{}/{}'.format(page.namespace.name, title)
            path = '{}/{}'.format(directory, title).replace('/tmp/', '')

        link = 'sdk_{}'.format(link.replace('/', '_').replace(' ', '_').replace('.', '_').lower())

        return (directory, path, title, link)

    def write_toctrees(self, toctrees):
        """ Write many Table Of Contents trees

        :param toctrees:
            Dict of the following format::

                {
                    "/path/where/toctree/will/be/placed": set(["Title of page to link to", "Title of page to link to", ...]),
                    ...
                }
        """
        for directory, values in toctrees.items():
            values = list(values)
            values = sorted(values)

            split = directory.split('/')
            title = ''
            if len(split) == 5:
                split = split[-2:]
                title = ' '.join(split).title()
            else:
                title = split[-1]

            data = '{}\n{}\n\n.. toctree::\n    :maxdepth: 1\n\n{}\n'.format(
                title,
                '=' * len(title),
                '\n'.join(['    {}'.format(value) for value in values])
            )

            if not os.path.exists(directory):
                os.makedirs(directory)

            print('{}/index.rst'.format(directory))
            with open('{}/index.rst'.format(directory), 'wb') as f:
                f.write(data.encode('utf-8'))

    def write_root_toctrees(self):
        """Writes toctrees for the top-level directories which don't already have one."""

        toctrees_to_write = {}

        for root, dirs, files in os.walk(self.BASE_DIR):
            if "index.rst" in files:
                # Folder already has an index
                continue

            toctrees_to_write[root] = set([dir + "/index" for dir in dirs \
                                            if dir not in self.DUPLICATES])

        self.write_toctrees(toctrees_to_write)

    def handle(self, *args, **options):
        base = self.BASE_DIR
        if os.path.exists(base):
            shutil.rmtree(base)

        all_pages = list(Page.objects.all()) + list(Element.objects.all())
        pages = []
        for page in all_pages:
            title = page.title if type(page) == Page else page.name
            if title not in self.DUPLICATES:
                pages.append(page)

        lang_toctrees = {}
        namespace_toctrees = {}
        link_fix = {
            '/sdk/apps/qml/QtQuick/Window.Window/': 'sdk_qtquick_window_window',
        }

        for page in pages:
            directory, path, title, link = self.paths(page)

            if page.namespace:
                if directory not in lang_toctrees:
                    lang_toctrees[directory] = set()

                lang_toctrees[directory].add('{}/index'.format(page.namespace.name))

                if directory not in namespace_toctrees:
                    namespace_toctrees[directory] = set()

                namespace_toctrees[directory].add(title)
            else:
                if directory not in lang_toctrees:
                    lang_toctrees[directory] = set()

                lang_toctrees[directory].add(title)

            link_fix['/{}/'.format(path)] = link

        self.write_toctrees(lang_toctrees)
        self.write_toctrees(namespace_toctrees)
        self.write_root_toctrees()

        for page in pages:
            if page.section.topic_version.language.topic.name != 'apps':
                continue

            directory, path, title, link = self.paths(page)
            header_title = title
            if page.namespace:
                header_title = '{} {}'.format(page.namespace.name, title)

            # For testing
            '''
            if title != 'Alarm':
                continue
            '''

            file_path = '{}/{}'.format(directory, title)
            file_path += '.rst'

            if not os.path.exists(directory):
                os.makedirs(directory)

            data = page.data.replace('/api', '/sdk')  # Fix base
            data = data.replace(' More...', '')  # Remove things that should be links but aren't

            # Strip version
            for lang in Language.objects.all():
                data = data.replace('{}/'.format(lang.development_version.name), '')

            # Clean up namespace links
            for namespace in Namespace.objects.all():
                data = data.replace('/{}.'.format(namespace.name), '/{}/'.format(namespace.name))

            # Convert to rst links
            for old, new in link_fix.items():
                data = data.replace(old, new)

            # Output to rst
            output = pypandoc.convert_text(data, 'rst', format='html', extra_args=[
                '--wrap', 'none',
                '--columns', '300',
            ], filters=[
                # Filter out blank links
                os.path.join(os.path.dirname(os.path.realpath(__file__)), 'filter.py')
            ])

            lines = output.split('\n')
            filtered_lines = []
            index = 0

            while index < len(lines):
                ok = True
                line = lines[index]

                if '<sdk_' in line:  # has a ref link to fix
                    replace_map = {}

                    reiter = re.finditer(r'`[^`<]+<sdk_', line)
                    for match in reiter:
                        start = match.start(0)
                        end = line.index('>', start) + 4

                        subline = line[start:end]

                        # Remove the -prop, etc
                        replace_subline = re.sub(r'-([\w\d-]+)>', '>', subline)
                        replace_subline = ':ref:{}'.format(replace_subline)
                        replace_subline = replace_subline.replace('`__', '`').replace('#', '_')

                        if '.' in replace_subline and replace_subline.index('<sdk') > replace_subline.index('.') and replace_subline.index('.') < replace_subline.index('>'):
                            # Only remove the . from inside the reference link
                            split = list(replace_subline)
                            for split_index in range(replace_subline.index('<sdk'), replace_subline.index('>')):
                                if split[split_index] == '.':
                                    split[split_index] = '_'

                            replace_subline = ''.join(split)

                        replace_map[subline] = replace_subline

                    for subline, replace_subline in replace_map.iteritems():
                        line = line.replace(subline, replace_subline)

                # Fix bad code blocks
                if line == '.. code:: code':
                    if page.section.topic_version.language.name == 'html5':
                        line = '.. code:: html'
                    else:
                        line = '.. code:: {}'.format(page.section.topic_version.language.name)

                # Don't include lines with one `|`
                if line.strip() == '|':
                    ok = False
                    index += 1

                # Skip images for now
                line = re.sub(r'\|image\d+\|', '', line)
                if line.startswith('..') and 'image::' in line:
                    ok = False
                    index += 1

                # Clean out needless raw html
                if line == '.. raw:: html':
                    if 'div' in lines[index + 2]:
                        ok = False
                        index += 3

                # Remove problematic rubrics
                if line.startswith('.. rubric::'):
                    ok = False
                    index += 2

                if ok:
                    filtered_lines.append(line)
                    index += 1

            lines = filtered_lines

            properties_line = None
            methods_line = None
            signals_line = None
            attached_properties_line = None
            attached_methods_line = None
            attached_signals_line = None

            detailed_description_line = None
            property_documentation_line = None
            method_documentation_line = None
            signal_documentation_line = None
            attached_properties_documentation_line = None
            attached_method_documentation_line = None
            attached_signal_documentation_line = None

            # Find locations of various subsections
            for index in range(0, len(lines)):
                line = lines[index]
                if line == 'Properties':
                    properties_line = index
                elif line == 'Methods':
                    methods_line = index
                elif line == 'Signals':
                    signals_line = index
                elif line == 'Attached Properties':
                    attached_properties_line = index
                elif line == 'Attached Methods':
                    attached_methods_line = index
                elif line == 'Attached Signals':
                    attached_signals_line = index
                elif line == 'Detailed Description':
                    detailed_description_line = index
                elif line == 'Property Documentation':
                    property_documentation_line = index
                elif line == 'Method Documentation':
                    method_documentation_line = index
                elif line == 'Signal Documentation':
                    signal_documentation_line = index
                elif line == 'Attached Property Documentation':
                    attached_properties_documentation_line = index
                elif line == 'Attached Method Documentation':
                    attached_method_documentation_line = index
                elif line == 'Attached Signal Documentation':
                    attached_signal_documentation_line = index

            possible_starts = [
                len(lines) - 1,
                properties_line,
                methods_line,
                signals_line,
                attached_properties_line,
                attached_methods_line,
                attached_signals_line,
            ]

            possible_ends = [
                len(lines) - 1,
                detailed_description_line,
                property_documentation_line,
                method_documentation_line,
                signal_documentation_line,
                attached_properties_documentation_line,
                attached_method_documentation_line,
                attached_signal_documentation_line,
            ]

            # Determin where to start looking for properties
            property_start = min([l for l in possible_starts if l is not None])
            property_end = min([l for l in possible_ends if l is not None])

            # Clean up properties
            index = property_start
            while index < property_end:
                index += 1
                line = lines[index]

                if line.strip().startswith('- '):
                    line = line.replace('**', '')
                    lines[index] = line

            refs = []

            # Add references to property definitions
            index = property_end
            while index < len(lines) - 1:
                index += 1
                line = lines[index]

                '''
                Example of what we are looking for:

                +--------------------------------------------------------------------------+
                | state : enumeration                                                      |
                +--------------------------------------------------------------------------+
                '''

                if line.startswith('| ') and not lines[index - 2].strip() and lines[index - 1].startswith('+-') and lines[index + 1].startswith('+-') and not lines[index + 2].strip():
                    # Clean up the names
                    ref = line.replace('|', '').replace('\\', '').replace('.', '_')
                    ref = ref.replace('[default]', '')
                    ref = ref.replace('[read-only]', '')
                    ref = ref.replace('{}_'.format(title), '')
                    ref = ref.split(':')[0]
                    ref = ref.split('(')[0]
                    ref = ref.strip().split(' ')[-1]
                    ref = ref.strip()
                    ref = '_{}_{}'.format(link, ref)

                    # Duplicate refs are not allowed
                    if ref in refs:
                        for i in range(1, 100):
                            if ref + str(i) not in refs:
                                ref += str(i)
                                break

                    refs.append(ref)
                    lines.insert(index - 2, '.. {}:'.format(ref))
                    index += 1

            data = '\n'.join(lines)
            data = data.replace('`__', '`_ ')  # Fix links
            data = data.replace('****', '**')  # Fix double emphasis

            if page.section.topic_version.language.name == 'html5':
                # Clean up html specific issues
                data = data.replace('**``', '**')
                data = data.replace('``**', '**')
                data = data.replace(' ``', '``')
                data = data.replace('`` ', '``')
                data = data.replace('````', '')
                data = data.replace('``**', '`` **')
                data = data.replace('``<', '`` <')

            data = re.sub(r'\n\s*\n', '\n\n', data)  # Remove extra lines
            lines = data.split('\n')

            # Balance tables (they may have been altered due to any of the above code)
            in_table = False
            start_line = 0
            table_length = 0
            for index in range(0, len(lines)):
                line = lines[index]
                if line.startswith('+-') and lines[index + 1].startswith('|') and not in_table:
                    in_table = True
                    table_length = len(line)
                    start_line = index
                elif line.startswith('+-') and not lines[index + 1].strip():
                    for table_index in range(start_line, index + 1):
                        table_line = lines[table_index]
                        if len(table_line) < table_length:
                            padding = table_length - len(table_line)
                            if table_line.startswith('+-'):
                                lines[table_index] = '{}{}+'.format(table_line[:-1], ('-' * padding))
                            elif table_line.startswith('+='):
                                lines[table_index] = '{}{}+'.format(table_line[:-1], ('=' * padding))
                            else:
                                lines[table_index] = '{}{}|'.format(table_line[:-1], (' ' * padding))

                    in_table = False

                if in_table:
                    if len(line) > table_length:
                        table_length = len(line)

            # Add the title line & reference
            data = '\n'.join(lines)
            header = '{}\n\n{}\n{}\n\n'.format(
                '.. _{}:'.format(link),
                header_title,
                '=' * len(header_title)
            )

            print(file_path)
            with open(file_path, 'wb') as f:
                f.write(header.encode('utf-8'))
                f.write(data.encode('utf-8'))
