# -*- coding: utf-8 -*-

from django.forms import ModelForm
from django.contrib.auth.models import User

from .models import Topic, Language, Version, Section, Namespace, Element, Page
from rest_framework.authtoken.models import Token

class TopicForm(ModelForm):
    class Meta:
        model = Topic


class LanguageForm(ModelForm):
    class Meta:
        model = Language


class VersionForm(ModelForm):
    class Meta:
        model = Version


class SectionForm(ModelForm):
    class Meta:
        model = Section


class NamespaceForm(ModelForm):
    class Meta:
        model = Namespace

    def __init__(self, *args, **kargs):
        if 'version' in kargs:
            version = kargs['version']
            del kargs['version']
        elif hasattr(self, 'instance') and self.instance.section:
            version = self.instance.section.topic_version
        else:
            version=None
        super(NamespaceForm, self).__init__(*args, **kargs)
        self.fields['platform_section'].queryset = Section.objects.filter(topic_version=version)


class PageForm(ModelForm):
    class Meta:
        model = Page

    def __init__(self, *args, **kargs):
        if 'version' in kargs:
            version = kargs['version']
            del kargs['version']
        elif hasattr(self, 'instance') and self.instance.section:
            version = self.instance.section.topic_version
        else:
            version=None
        super(PageForm, self).__init__(*args, **kargs)
        self.fields['section'].queryset = Section.objects.filter(topic_version=version)
        self.fields['namespace'].queryset = Namespace.objects.filter(platform_section__topic_version=version)


class ElementForm(ModelForm):
    class Meta:
        model = Element

    def __init__(self, *args, **kargs):
        if 'version' in kargs:
            version = kargs['version']
            del kargs['version']
        elif hasattr(self, 'instance') and self.instance.section:
            version = self.instance.section.topic_version
        else:
            version=None
        super(ElementForm, self).__init__(*args, **kargs)
        self.fields['section'].queryset = Section.objects.filter(topic_version=version)
        self.fields['namespace'].queryset = Namespace.objects.filter(platform_section__topic_version=version)


class TokenForm(ModelForm):
    class Meta:
        model = Token
        fields = ('user',)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username',)
