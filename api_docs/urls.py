from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = staticfiles_urlpatterns()


urlpatterns += patterns('',
   
    # REST framework
    url(r'^\+service/$', 'api_docs.views.token_edit', name='token_edit'),
    url(r'^\+service/(?P<token_key>[\d\w]+)/$', 'api_docs.views.token_edit', name='token_edit'),

    url(r'^$', 'api_docs.views.overview', name='overview'),

    url(r'^(?P<topic_name>[\w\.-]+)/$', 'api_docs.views.topic_view', name='topic'),
    url(r'^\+topic/$', 'api_docs.views.topic_edit', name='topic_edit'),
    url(r'^\+topic/(?P<topic_id>[\d]+)/$', 'api_docs.views.topic_edit', name='topic_edit'),

    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/$', 'api_docs.views.language_view', name='language'),
    url(r'^(?P<topic_name>[\w\.-]+)/\+language/$', 'api_docs.views.language_edit', name='language_edit'),
    url(r'^(?P<topic_name>[\w\.-]+)/\+language/(?P<language_id>[\d]+)/$', 'api_docs.views.language_edit', name='language_edit'),

    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/$', 'api_docs.views.version_view', name='version'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/\+version/$', 'api_docs.views.version_edit', name='version_edit'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/\+version/(?P<version_id>[\d]+)/$', 'api_docs.views.version_edit', name='version_edit'),

    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<version_name>[\w\.-]+)/\+section/(?P<section_id>[\d]+)/$', 'api_docs.views.section_edit', name='section_edit'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<version_name>[\w\.-]+)/\+section/$', 'api_docs.views.section_edit', name='section_edit'),

    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<version_name>[\w\.-]+)/\+namespace/(?P<namespace_id>[\d]+)/$', 'api_docs.views.namespace_edit', name='namespace_edit'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<version_name>[\w\.-]+)/\+namespace/$', 'api_docs.views.namespace_edit', name='namespace_edit'),

    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/search/$', 'api_docs.views.search', name='search'),

    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/(?P<element_fullname>[\w\.\-\:]+)/$', 'api_docs.views.element_view', name='element'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/\+element/(?P<element_id>[\d]+)/$', 'api_docs.views.element_edit', name='element_edit'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/\+element/$', 'api_docs.views.element_edit', name='element_edit'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/\+page/(?P<page_id>[\d]+)/$', 'api_docs.views.page_edit', name='page_edit'),
    url(r'^(?P<topic_name>[\w\.-]+)/(?P<language_name>[\w\.-]+)/(?P<release_version>[\w\.-]+)/\+page/$', 'api_docs.views.page_edit', name='page_edit'),

)


