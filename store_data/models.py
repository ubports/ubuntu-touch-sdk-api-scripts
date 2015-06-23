from django.db import models

# Create your models here.


class Release(models.Model):
    name = models.CharField(max_length=25)


class Architecture(models.Model):
    name = models.CharField(max_length=10)


class GadgetSnap(models.Model):
    icon_url = models.URLField(blank=True)
    release = models.ManyToManyField(Release)
    name = models.CharField(max_length=50)
    ratings_average = models.DecimalField(max_digits=2, decimal_places=1)
    alias = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    publisher = models.CharField(max_length=50)
    store_url = models.URLField(blank=True)
    publisher = models.CharField(max_length=10)
    version = models.CharField(max_length=15)
    architecture = models.ManyToManyField(Architecture)
    title = models.CharField(max_length=30)
    last_updated = models.DateTimeField()
