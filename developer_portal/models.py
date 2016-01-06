from django.db import models

from cms.extensions import TitleExtension
from cms.extensions.extension_pool import extension_pool
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


class SEOExtension(TitleExtension):
    keywords = models.CharField(max_length=256)

extension_pool.register(SEOExtension)
