from .models import Topic, Language, Version, Section, Namespace, Element, Page
from django.contrib import admin

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
admin.site.register(Topic, TopicAdmin)

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'topic', 'current_version', 'development_version')
    list_filter = ('topic',)
    search_fields = ('name', 'slug')
admin.site.register(Language, LanguageAdmin)

class VersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'language')
    list_filter = ('language__topic', 'language',)
    search_fields = ('name', 'slug')

admin.site.register(Version, VersionAdmin)

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic_version')
    list_filter = ('topic_version__language', 'topic_version')
    search_fields = ('name', 'description')
admin.site.register(Section, SectionAdmin)

class NamespaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform_section', )
    list_filter = ('platform_section__topic_version__language', 'platform_section__topic_version')
    search_fields = ('name', )
admin.site.register(Namespace, NamespaceAdmin)

class ElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'namespace', 'section')
    list_filter = ('section__topic_version__language', 'section__topic_version', 'section', 'namespace')
    search_fields = ('name', 'fullname', 'description')
admin.site.register(Element, ElementAdmin)

class PageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'namespace', 'section')
    list_filter = ('section__topic_version__language', 'section__topic_version', 'section', 'namespace')
    search_fields = ('slug', 'title', 'fullname', 'description')
admin.site.register(Page, PageAdmin)
