from django.conf.urls import url, patterns, include
from rest_framework import routers
from service.views import *

# Routers provide an easy way of automatically determining the URL conf
router = routers.DefaultRouter()
router.register(r'elements', ElementViewSet, base_name='element-list')
router.register(r'pages', PageViewSet, base_name='page-list')
router.register(r'namespaces', NamespaceViewSet, base_name='namespace-list')
router.register(r'sections', SectionViewSet, base_name='section-list')
router.register(r'versions', VersionViewSet, base_name='version-list')
router.register(r'languages', LanguageViewSet, base_name='language-list')
router.register(r'topics', TopicViewSet, base_name='topic-list')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
