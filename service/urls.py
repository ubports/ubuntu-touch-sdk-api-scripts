from django.conf.urls import url, patterns, include
from rest_framework import routers
from service.views import *

# Routers provide an easy way of automatically determining the URL conf
router = routers.DefaultRouter()
router.register(r'elements', ElementViewSet)
router.register(r'pages', PageViewSet)
router.register(r'namespaces', NamespaceViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'versions', VersionViewSet)
router.register(r'languages', LanguageViewSet)
router.register(r'topics', TopicViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
