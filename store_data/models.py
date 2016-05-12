from django.db import models


class Release(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class Architecture(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class ScreenshotURL(models.Model):
    url = models.URLField(blank=True)

    def __str__(self):
        return self.url


class GadgetSnap(models.Model):
    icon_url = models.URLField(blank=True, null=True)
    release = models.ManyToManyField(Release)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=250, blank=True, null=True)
    ratings_average = models.DecimalField(max_digits=2, decimal_places=1)
    alias = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    publisher = models.CharField(max_length=100)
    store_url = models.URLField(blank=True)
    version = models.CharField(max_length=25)
    architecture = models.ManyToManyField(Architecture)
    last_updated = models.DateTimeField()
    description = models.TextField(max_length=5000)
    screenshot_url = models.ManyToManyField(ScreenshotURL, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name
