from django.contrib import admin

from reversion.models import Revision, Version
from reversion.admin import VersionAdmin

from cms.extensions import TitleExtensionAdmin
from .models import (
    ExternalDocsBranch, ExternalDocsBranchImportDirective,
    ImportedArticle, SEOExtension
)
from django.core.management import call_command

__all__ = (
)


def import_selected_external_docs_branches(modeladmin, request, queryset):
    branches = []
    for branch in queryset:
        branches.append(branch.origin)
    call_command('import-external-docs-branches', *branches)
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


@admin.register(ExternalDocsBranch)
class ExternalDocsBranchAdmin(admin.ModelAdmin):
    list_display = ('origin', 'post_checkout_command', 'branch_name',)
    list_filter = ('origin', 'post_checkout_command', 'branch_name',)
    actions = [import_selected_external_docs_branches]


@admin.register(ExternalDocsBranchImportDirective)
class ExternalDocsBranchImportDirectiveAdmin(admin.ModelAdmin):
    pass

@admin.register(ImportedArticle)
class ImportedArticleAdmin(admin.ModelAdmin):
    pass

class SEOExtensionAdmin(TitleExtensionAdmin):
    pass

admin.site.register(SEOExtension, SEOExtensionAdmin)
