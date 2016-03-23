from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = staticfiles_urlpatterns()


urlpatterns += patterns('',
   
    # REST framework
    url(r'^$', 'api_docs.views.overview', name='overview'),
    url(r'^(?P<topic_name>[\w\.-]+)/$', 'api_docs.views.topic_view', name='topic'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/$', 'api_docs.views.language_view', name='language'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/$', 'api_docs.views.version_view', name='version'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/\+release/$', 'api_docs.views.release_version', name='release_version'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/(?P<element_fullname>[\w\.\-\:]+)/$', 'api_docs.views.element_view', name='element'),
    
)


