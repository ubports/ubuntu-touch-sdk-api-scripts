from django.db import models


class Release(models.Model):
    name = models.CharField(max_length=25)


class Architecture(models.Model):
    name = models.CharField(max_length=10)


class GadgetSnap(models.Model):
    icon_url = models.URLField(blank=True)
    release = models.ManyToManyField(Release)
    name = models.CharField(max_length=100)
    ratings_average = models.DecimalField(max_digits=2, decimal_places=1)
    alias = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    publisher = models.CharField(max_length=100)
    store_url = models.URLField(blank=True)
    version = models.CharField(max_length=25)
    architecture = models.ManyToManyField(Architecture)
    title = models.CharField(max_length=50)
    last_updated = models.DateTimeField()
