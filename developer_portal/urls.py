from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from developer_portal.views import login_failure, listen_for_login

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout$', 'developer_portal.views.site_logout', name='logout')
)

urlpatterns += patterns(
    'django_openid_auth.views',
    url(r'^openid/login/$', 'login_begin', name='openid-login',
        kwargs={'render_failure': login_failure}),
    url(r'^openid/complete/$', 'login_complete', name='openid-complete',
        kwargs={'render_failure': login_failure}),
    url(r'^openid/logo.gif$', 'logo', name='openid-logo'),
    url(r'^api/service/', include('service.urls', namespace='rest_framework')),
    url(r'^api/', include('api_docs.urls', namespace='api_docs')),
)
listen_for_login()

urlpatterns += i18n_patterns('',
    url(r'^blog/', include('developer_portal.blog.urls', namespace='zinnia')),
    url(r'^blog/comments/', include('django_comments.urls')),
)

urlpatterns += i18n_patterns('',
    url(r'^search/', 'developer_portal.views.search', name='search'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^', include('cms.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('webapp_creator.views',
                       url(r'^webapp-generator/$', 'webapp', name='webapp'),
)

urlpatterns += patterns('translations_dashboard.views',
                       url(r'^translations-dashboard/$', 'translations_dashboard', name='translations_dashboard'),
)
