from django.contrib import admin
from .models import PathMatchRedirect

# Register your models here.

@admin.register(PathMatchRedirect)
class PathMatchRedirectAdmin(admin.ModelAdmin):
    list_display = ('match', 'replace', 'preserve_extra')
    exclude = ('precedence',)
