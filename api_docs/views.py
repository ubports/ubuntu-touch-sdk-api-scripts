# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.models import User, Group

from .models import Topic, Language, Version, Section, Namespace, Element, Page
from rest_framework.authtoken.models import Token

from forms import *

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


def topic_edit(request, topic_id=0):
    if topic_id:
        topic = get_object_or_404(Topic, id=topic_id)
    else:
        topic = Topic()

    if not request.user.has_perm('common.change_topic'):
        return HttpResponseRedirect(reverse(topic_view, args=[topic.slug]))

    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(topic_view, args=[topic.slug]))
    else:
        form = TopicForm(instance=topic)
    context = {
        'form': form,
        'topic': topic,
    }
    return render_to_response('api_docs/topic_edit.html', context, RequestContext(request))


def language_view(request, topic_name, language_name):
    language = get_object_or_404(Language, topic__slug=topic_name, slug=language_name)

    context = {
        'topic': language.topic,
        'language': language,
    }
    return render_to_response('api_docs/language.html', context, RequestContext(request))


def language_edit(request, topic_name, language_id=0):
    if language_id:
        language = get_object_or_404(Language, id=language_id)
    else:
        language = Language()

    if not request.user.has_perm('common.change_language'):
        return HttpResponseRedirect(reverse(language_view, args=[language.slug]))

    if request.method == 'POST':
        form = LanguageForm(request.POST, instance=language)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(language_view, args=[language.topic.slug, language.slug]))
    else:
        form = LanguageForm(instance=language)
    context = {
        'form': form,
        'topic': language.topic,
        'language': language,
    }
    return render_to_response('api_docs/language_edit.html', context, RequestContext(request))


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
            section_size = section.namespace_set.count() + section.free_element_set().count() + 2  # Extra 2 for the section header
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


def version_edit(request, topic_name, language_name, version_id=0):
    if version_id:
        version = get_object_or_404(Version, language__topic__slug=topic_name, language__slug=language_name, id=version_id)
        language = version.language
        topic = language.topic
    else:
        topic = get_object_or_404(Topic, slug=topic_name)
        language = get_object_or_404(Language, topic__slug=topic_name, slug=language_name)
        version = Version(language=language)

    if not request.user.has_perm('common.change_version'):
        return HttpResponseRedirect(reverse(version_view, args=[topic.slug, version.slug]))

    if request.method == 'POST':
        form = VersionForm(request.POST, instance=version)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(version_view, args=[topic.slug, language.slug, version.slug]))
    else:
        form = VersionForm(instance=version)
    context = {
        'form': form,
        'topic': topic,
        'language': language,
        'version': version,
    }
    return render_to_response('api_docs/version_edit.html', context, RequestContext(request))


def section_edit(request, topic_name, language_name, version_name, section_id=0):
    if section_id:
        section = get_object_or_404(Section, topic_version__language__topic__slug=topic_name, topic_version__language__slug=language_name, topic_version__slug=version_name, id=section_id)
        version = section.topic_version
        language = version.language
        topic = language.topic
    else:
        topic = get_object_or_404(Topic, slug=topic_name)
        language = get_object_or_404(Language, topic__slug=topic_name, slug=language_name)
        version = get_object_or_404(Version, language=language, slug=version_name)
        section = Section(topic_version=version)

    if not request.user.has_perm('common.change_section'):
        return HttpResponseRedirect(reverse(version_view, args=[topic.slug, language.slug, version.slug]))

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(version_view, args=[topic.slug, language.slug, version.slug]))
    elif request.GET.get('action', None) == 'delete':
        context = {
            'sidenav': topic_name,
            'topic': topic,
            'language': language,
            'version': version,
            'type': 'section',
            'name': section.name,
        }
        return render_to_response('api_docs/delete_confirm.html', context, RequestContext(request))

    elif request.GET.get('action', None) == 'delete_cancel':
        return HttpResponseRedirect(reverse(version_view, args=[topic_name, language.slug, version_name]))

    elif request.GET.get('action', None) == 'delete_confirm':
        section.delete()
        return HttpResponseRedirect(reverse(version_view, args=[topic_name, language.slug, version_name]))

    else:
        form = SectionForm(instance=section)
    context = {
        'sidenav': topic_name,
        'form': form,
        'topic': topic,
        'language': language,
        'version': version,
        'section': section,
    }
    return render_to_response('api_docs/section_edit.html', context, RequestContext(request))

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


def namespace_edit(request, topic_name, version_name, namespace_id=0):
    if namespace_id:
        namespace = get_object_or_404(Namespace, platform_section__topic_version__slug=version_name, platform_section__topic_version__topic__slug=topic_name, id=namespace_id)
        version = namespace.platform_section.topic_version
        topic = version.topic
    else:
        topic = get_object_or_404(Topic, slug=topic_name)
        version = get_object_or_404(Version, slug=version_name, topic=topic)
        namespace = Namespace()

    if not request.user.has_perm('apidocs.change_namespace'):
        return HttpResponseRedirect(reverse(element_view, args=[topic_name, version_name, namespace.name]))

    if request.method == 'POST':
        form = NamespaceForm(request.POST, instance=namespace, version=version)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(element_view, args=[topic_name, version_name, namespace.name]))
    elif request.GET.get('action', None) == 'delete':
        context = {
            'sidenav': topic_name,
            'topic': topic,
            'language': version.language,
            'version': version,
            'name': namespace.name,
            'type': 'Namespace',
        }
        return render_to_response('api_docs/delete_confirm.html', context, RequestContext(request))

    elif request.GET.get('action', None) == 'delete_cancel':
        return HttpResponseRedirect(reverse(element_view, args=[topic_name, version_name, namespace.name]))

    elif request.GET.get('action', None) == 'delete_confirm':
        namespace.delete()
        return HttpResponseRedirect(reverse(version_view, args=[topic_name, version_name]))

    else:
        form = NamespaceForm(instance=namespace, version=version)
    context = {
        'form': form,
        'sidenav': topic_name,
        'topic': topic,
        'language': version.language,
        'version': version,
        'namespace': namespace,
    }
    return render_to_response('api_docs/namespace_edit.html', context, RequestContext(request))

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


def page_edit(request, topic_name, language_name, release_version, page_id=0):
    if page_id:
        page = get_object_or_404(Page, section__topic_version__slug=release_version, section__topic_version__language__slug=language_name, section__topic_version__language__topic__slug=topic_name, id=page_id)
        version = page.section.topic_version
        topic = version.language.topic
    else:
        topic = get_object_or_404(Topic, slug=topic_name)
        version = get_object_or_404(Version, slug=release_version, language__slug=language_name, topic=topic)
        page = Page()

    if not request.user.has_perm('apidocs.change_page'):
        return HttpResponseRedirect(reverse(version_view, args=[topic_name, release_version]))

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page, version=version)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(version_view, args=[topic_name, release_version]))
    elif request.GET.get('action', None) == 'delete':
        context = {
            'sidenav': topic_name,
            'topic': topic,
            'language': version.language,
            'version': version,
            'name': page.title,
            'type': 'Page',
        }
        return render_to_response('api_docs/delete_confirm.html', context, RequestContext(request))
        
    elif request.GET.get('action', None) == 'delete_cancel':
        return HttpResponseRedirect(reverse(element_view, args=[topic_name, release_version, page.fullname]))
        
    elif request.GET.get('action', None) == 'delete_confirm':
        page.delete()
        return HttpResponseRedirect(reverse(version_view, args=[topic_name, release_version]))
        
    else:
        form = PageForm(instance=page, version=version)
    context = {
        'form': form,
        'sidenav': topic_name,
        'topic': topic,
        'language': version.language,
        'version': version,
        'page': page,
    }
    return render_to_response('api_docs/page_edit.html', context, RequestContext(request))


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


def element_edit(request, topic_name, release_version, element_id=0):

    if element_id:
        element = get_object_or_404(Element, section__topic_version__slug=release_version, section__topic_version__topic__slug=topic_name, id=element_id)
        version = element.section.topic_version
        topic = version.topic
    else:
        topic = get_object_or_404(Topic, slug=topic_name)
        version = get_object_or_404(Version, slug=release_version, topic=topic)
        element = Element()

    if not request.user.has_perm('apidocs.change_element'):
        return HttpResponseRedirect(reverse(element_view, args=[topic_name, release_version, element.fullname]))

    if request.method == 'POST':
        form = ElementForm(request.POST, instance=element, version=version)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(element_view, args=[topic_name, release_version, element.fullname]))
    elif request.GET.get('action', None) == 'delete':
        context = {
            'sidenav': topic_name,
            'topic': topic,
            'language': version.language,
            'version': version,
            'name': element.fullname,
            'type': 'Element',
        }
        return render_to_response('api_docs/delete_confirm.html', context, RequestContext(request))

    elif request.GET.get('action', None) == 'delete_cancel':
        return HttpResponseRedirect(reverse(element_view, args=[topic_name, release_version, element.fullname]))

    elif request.GET.get('action', None) == 'delete_confirm':
        element.delete()
        return HttpResponseRedirect(reverse(version_view, args=[topic_name, release_version]))

    else:
        form = ElementForm(instance=element, version=version)
    context = {
        'form': form,
        'sidenav': topic_name,
        'topic': topic,
        'language': version.language,
        'version': version,
        'element': element,
    }
    return render_to_response('api_docs/element_edit.html', context, RequestContext(request))


def search(request, topic_name, language_name, release_version):
    version = _get_release_version(topic_name, language_name, release_version)
    query = request.GET.get('query', '')
    results = Element.objects.filter(section__topic_version=version, name__icontains=query).order_by('section', 'fullname')

    context = {
        'sidenav': topic_name,
        'topic': version.language.topic,
        'language': version.language,
        'version': version,
        'query': query,
        'results': results
    }
    return render_to_response('api_docs/search.html', context, RequestContext(request))


def token_edit(request, token_key=None):
    if token_key:
        token = get_object_or_404(Token, key=token_key)
        if request.GET.get('action') == 'delete':
            token.delete()
            return HttpResponseRedirect(reverse('api_docs:token_edit', args=[]))
        elif request.GET.get('action') == 'reset':
            token.delete()
            token.key = token.generate_key()
            token.save()
            return HttpResponseRedirect(reverse('api_docs:token_edit', args=[]))
    token = Token()

    if not request.user.has_perm('authtoken.change_token'):
        return HttpResponseRedirect(reverse('api_docs:overview', args=[]))

    if request.method == 'POST':
        if request.POST.get('form') == 'token':
            form = TokenForm(request.POST, instance=token)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('api_docs:token_edit', args=[]))
        elif request.POST.get('form') == 'user':
            user, created = User.objects.get_or_create(username=request.POST.get('username'))
            if not created:
                return HttpResponseRedirect(reverse('api_docs:token_edit', args=[]))
            else:
                group = Group.objects.get(name='api-website-importers')
                user.groups.add(group)
                token = Token(user=user)
                token.save()
                return HttpResponseRedirect(reverse('api_docs:token_edit', args=[]))
    else:
        form = TokenForm(instance=token)

    tokens = Token.objects.all()
    context = {
        'form': form,
        'adduser': UserForm(),
        'token': token,
        'tokens': tokens,
    }
    return render_to_response('api_docs/token_edit.html', context, RequestContext(request))
