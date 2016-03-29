from .models import (
    Architecture,
    Release,
    GadgetSnap,
    ScreenshotURL,
)
from django.contrib import admin


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
admin.site.register(Release, ReleaseAdmin)


class ArchitectureAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
admin.site.register(Architecture, ArchitectureAdmin)


class GadgetSnapAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'alias', 'publisher')
admin.site.register(GadgetSnap, GadgetSnapAdmin)


@admin.register(ScreenshotURL)
class ScreenshotURLAdmin(admin.ModelAdmin):
    pass
