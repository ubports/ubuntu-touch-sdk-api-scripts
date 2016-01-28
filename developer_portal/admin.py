from django.contrib import admin

from reversion.models import Revision, Version
from reversion.admin import VersionAdmin

from cms.extensions import TitleExtensionAdmin
from .models import SEOExtension

__all__ = (
)


class RevisionAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'user', 'comment')
    list_display_links = ('date_created', )
    list_filter = ('user', )
    search_fields = ('user', 'comment')

admin.site.register(Revision, RevisionAdmin)


class VersionAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id')
    list_display_links = ('object_id', )
    list_filter = ('content_type', )

admin.site.register(Version, VersionAdmin)


class SEOExtensionAdmin(TitleExtensionAdmin):
    pass

admin.site.register(SEOExtension, SEOExtensionAdmin)
