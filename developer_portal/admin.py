from django.contrib import admin

from reversion.models import Revision, Version
from reversion.admin import VersionAdmin

from cms.extensions import TitleExtensionAdmin
from .models import ExternalDocsBranch, SEOExtension
from django.core.management import call_command

__all__ = (
)


def import_selected_external_docs_branches(modeladmin, request, queryset):
    for branch in queryset:
        call_command('import-external-docs-branches', branch.docs_namespace)
    import_selected_external_docs_branches.short_description = \
        "Import selected branches"


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


class ExternalDocsBranchAdmin(admin.ModelAdmin):
    list_display = ('lp_origin', 'docs_namespace')
    list_filter = ('lp_origin', 'docs_namespace')
    actions = [import_selected_external_docs_branches]

admin.site.register(ExternalDocsBranch, ExternalDocsBranchAdmin)

class SEOExtensionAdmin(TitleExtensionAdmin):
    pass

admin.site.register(SEOExtension, SEOExtensionAdmin)
