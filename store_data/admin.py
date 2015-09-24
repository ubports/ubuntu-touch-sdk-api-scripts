from .models import Release, Architecture, GadgetSnap
from django.contrib import admin

# Register your models here.


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
