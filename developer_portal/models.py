from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from djangocms_text_ckeditor.html import extract_images
from djangocms_text_ckeditor.models import AbstractText


class RawHtml(AbstractText):

    class Meta:
        abstract = False

    def save(self, *args, **kwargs):
        body = self.body
        body = extract_images(body, self)
        self.body = body
        AbstractText.save(self, *args, **kwargs)


class ExternalDocsBranch(models.Model):
    lp_origin = models.CharField(
        max_length=200,
        help_text=_('Launchpad branch location, ie: lp:snappy/15.04'))
    docs_namespace = models.CharField(
        max_length=120,
        help_text=_('Path alias we want to use for the docs, '
                    'ie "snappy/guides/15.04" or "snappy/guides/latest", etc.'))
