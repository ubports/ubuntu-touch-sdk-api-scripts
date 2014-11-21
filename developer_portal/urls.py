from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = i18n_patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^blog/entries/', include('zinnia.urls', namespace='zinnia')),
    url(r'^blog/comments/', include('django_comments.urls')),
    url(r'^', include('cms.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

