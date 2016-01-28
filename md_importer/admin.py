from django.contrib import admin

from .models import (
    ExternalDocsBranch, ExternalDocsBranchImportDirective,
    ImportedArticle,
)
from django.core.management import call_command

__all__ = (
)


def import_selected_external_docs_branches(modeladmin, request, queryset):
    branches = []
    for branch in queryset:
        branches.append(branch.origin)
    call_command('import_md', *branches)
    import_selected_external_docs_branches.short_description = \
        "Import selected branches"


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
