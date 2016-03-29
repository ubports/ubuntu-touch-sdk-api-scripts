from .models import (
    Architecture,
    GadgetSnap,
    Release,
    ScreenshotURL,
)
from django.contrib import admin


@admin.register(Architecture)
class ArchitectureAdmin(admin.ModelAdmin):
    pass


@admin.register(GadgetSnap)
class GadgetSnapAdmin(admin.ModelAdmin):
    pass


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    pass


@admin.register(ScreenshotURL)
class ScreenshotURLAdmin(admin.ModelAdmin):
    pass
