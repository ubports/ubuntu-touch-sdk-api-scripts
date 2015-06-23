from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = staticfiles_urlpatterns()

from django.contrib import admin
admin.autodiscover()
