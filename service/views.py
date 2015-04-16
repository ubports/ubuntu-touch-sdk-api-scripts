# Create your views here.
from api_docs.models import Topic, Language, Version, Section, Element, Page, Namespace
from rest_framework import viewsets, permissions, serializers
from rest_framework.reverse import reverse

class SimpleQuerySetFilterMixin(object):
    def get_queryset(self):
        search_values = getSearchValues(self.model, self.request.GET.items())
        return self.model.objects.filter(**search_values)
    
# Element
class ElementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Element
        extra_kwargs = {
            'url': {'view_name': 'rest_framework:element-detail'},
            'namespace': {'view_name': 'rest_framework:namespace-detail'},
            'section': {'view_name': 'rest_framework:section-detail'},
        }

class ElementViewSet(SimpleQuerySetFilterMixin, viewsets.ModelViewSet):
    """
    Provides a list of API Elements (Classes, Enums, etc)
    
    You can filter the list using the field names of an Element, optionally
    with a Django QuerySet suffix such as <field>__icontains
    """
    model = Element
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = ElementSerializer

# Page
class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        extra_kwargs = {
            'url': {'view_name': 'rest_framework:page-detail'},
            'namespace': {'view_name': 'rest_framework:namespace-detail'},
            'section': {'view_name': 'rest_framework:section-detail'},
        }

class PageViewSet(SimpleQuerySetFilterMixin, viewsets.ModelViewSet):
    model = Page
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = PageSerializer

# Namespace
class NamespaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Namespace
        extra_kwargs = {
            'url': {'view_name': 'rest_framework:namespace-detail'},
            'platform_section': {'view_name': 'rest_framework:section-detail'},
        }

class NamespaceViewSet(SimpleQuerySetFilterMixin, viewsets.ModelViewSet):
    model = Namespace
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = NamespaceSerializer

# Section
class SectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Section
        extra_kwargs = {
            'url': {'view_name': 'rest_framework:section-detail'},
            'topic_version': {'view_name': 'rest_framework:version-detail'},
        }

class SectionViewSet(SimpleQuerySetFilterMixin, viewsets.ReadOnlyModelViewSet):
    model = Section
    serializer_class = SectionSerializer

# Version
class VersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Version
        extra_kwargs = {
            'url': {'view_name': 'rest_framework:version-detail'},
            'language': {'view_name': 'rest_framework:language-detail'},
        }

class VersionViewSet(SimpleQuerySetFilterMixin, viewsets.ReadOnlyModelViewSet):
    model = Version
    serializer_class = VersionSerializer

# Language
class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        extra_kwargs = {
            'url': {'view_name': 'rest_framework:language-detail'},
            'topic': {'view_name': 'rest_framework:topic-detail'},
            'current_version': {'view_name': 'rest_framework:version-detail'},
            'development_version': {'view_name': 'rest_framework:version-detail'},
        }

class LanguageViewSet(SimpleQuerySetFilterMixin, viewsets.ReadOnlyModelViewSet):
    model = Language
    serializer_class = LanguageSerializer

# Topic
class TopicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Topic
        extra_kwargs = {
            'url': {'view_name': 'rest_framework:topic-detail'},
        }

class TopicViewSet(SimpleQuerySetFilterMixin, viewsets.ReadOnlyModelViewSet):
    model = Topic
    serializer_class = TopicSerializer

def getSearchValues(model, items):
    searchable_fields = [f.name for f in model._meta.local_fields+model._meta.many_to_many if not f.name.endswith("_ptr")]
    return dict([(str(key), value) for (key, value) in items if str(key).split('__')[0] in searchable_fields])
    
