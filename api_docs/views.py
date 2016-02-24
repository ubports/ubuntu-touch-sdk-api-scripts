# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User, Group

from .models import Topic, Language, Version, Section, Namespace, Element, Page

def _get_release_version(topic_name, language_name, release_version):
    try:
        language = Language.objects.get(topic__slug=topic_name, slug=language_name)
        if release_version == 'current':
            if language is not None and language.current_version is not None:
                version = language.current_version
                return version
        elif release_version == 'development':
            if language is not None and language.development_version is not None:
                version = language.development_version
                return version
    except:
        pass

    return get_object_or_404(Version, language__topic__slug=topic_name, language__slug=language_name, slug=release_version)
    

def overview(request):
    topics = Topic.objects.all()

    context = {
        'topics': topics,
    }
    return render_to_response('api_docs/overview.html', context, RequestContext(request))


def topic_view(request, topic_name):
    topic = get_object_or_404(Topic, slug=topic_name)

    context = {
        'topic': topic,
    }
    return render_to_response('api_docs/topic.html', context, RequestContext(request))


def language_view(request, topic_name, language_name):
    language = get_object_or_404(Language, topic__slug=topic_name, slug=language_name)

    context = {
        'topic': language.topic,
        'language': language,
    }
    return render_to_response('api_docs/language.html', context, RequestContext(request))

from django.forms import ModelForm
class VersionForm(ModelForm):
    class Meta:
        model = Version
        fields = ['name', 'slug']

def release_version(request, topic_name, language_name):
    language = get_object_or_404(Language, topic__slug=topic_name, slug=language_name)

    version = Version(language=language)

    if request.method == 'POST':
        form = VersionForm(request.POST, instance=version)
        if form.is_valid():
            form.save()
            language.current_version = language.development_version
            language.development_version = version
            language.save()
            version.import_from(language.current_version)
            version.save()
            return HttpResponseRedirect(reverse('api_docs:version', args=[topic_name, language_name, version.slug]))
    else:
        form = VersionForm(instance=version)
        
    context = {
        'form': form,
        'topic': language.topic,
        'language': language,
        'version': version,
        'previous': language.development_version,
    }
    return render_to_response('api_docs/version_edit.html', context, RequestContext(request))

def version_view(request, topic_name, language_name, release_version):
    version = _get_release_version(topic_name, language_name, release_version)

    sections = version.section_set.all()
    first_column = []
    second_column = []
    if len(sections) > 1:
        total_size = 0
        sorted_sections = []
        for section in sections:
            section_count = section.namespace_set.count()
            section_count += section.free_element_set().count()
            section_count += section.free_page_set().count()
            if section_count == 0 and not request.user.has_perm('common.change_version'):
                continue
            total_size += section_count + 2 # Extra 2 for the section header
            i = 0
            for s in sorted_sections:
                if (s.namespace_set.count() + s.free_element_set().count()) > section_count:
                    i += 1
                else:
                    break
            sorted_sections.insert(i, section)

        first_column_size = 0
        for section in sorted_sections:
            section_size = section.namespace_set.count() + section.free_element_set().count() + section.free_page_set().count() + 2  # Extra 2 for the section header
            if (first_column_size + section_size) <= (total_size / 2):
                first_column.append(section)
                first_column_size += (section_size)
            else:
                second_column.append(section)
    elif len(sections) == 1:
        first_column.append(sections[0])
        
    context = {
        'sidenav': topic_name,
        'topic': version.language.topic,
        'language': version.language,
        'version': version,
        'first_column': first_column,
        'second_column': second_column,
    }
    return render_to_response('api_docs/version.html', context, RequestContext(request))


def namespace_view(request, topic_name, language_name, release_version, namespace_name):
    version = _get_release_version(topic_name, language_name, release_version)
    
    try:
        namespace = Namespace.objects.get(platform_section__topic_version=version, name=namespace_name)
    except Namespace.MultipleObjectsReturned:
        namespace = Namespace.objects.filter(platform_section__topic_version=version, name=namespace_name)[0]
    except Namespace.DoesNotExist:
        return page_view(request, topic_name, language_name, release_version, namespace_name)

    context = {
        'sidenav': topic_name,
        'topic': version.language.topic,
        'language': version.language,
        'version': version,
        'namespace': namespace,
    }
    return render_to_response('api_docs/namespace.html', context, RequestContext(request))


def page_view(request, topic_name, language_name, release_version, page_fullname):
    version = _get_release_version(topic_name, language_name, release_version)

    page = get_object_or_404(Page, section__topic_version=version, fullname=page_fullname)

    context = {
        'sidenav': topic_name,
        'topic': version.language.topic,
        'language': version.language,
        'version': version,
        'page': page,
    }
    return render_to_response('api_docs/page.html', context, RequestContext(request))


def element_view(request, topic_name, language_name, release_version, element_fullname):
    version = _get_release_version(topic_name, language_name, release_version)

    try:
        element = Element.objects.get(section__topic_version=version, fullname=element_fullname)
    except Element.MultipleObjectsReturned:
        element = Element.objects.filter(section__topic_version=version, fullname=element_fullname)[0]
    except Element.DoesNotExist:
        return namespace_view(request, topic_name, language_name, release_version, element_fullname)

    context = {
        'sidenav': topic_name,
        'topic': version.language.topic,
        'language': version.language,
        'version': version,
        'element': element,
    }
    return render_to_response('api_docs/element.html', context, RequestContext(request))
