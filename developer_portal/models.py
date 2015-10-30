from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
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


class ExternalDocsBranch(models.Model):
    # We originally assumed that branches would also live in LP,
    # well, we were wrong, but let's keep the name around. It's
    # no use having a schema/data migration just for this.
    lp_origin = models.CharField(
        max_length=200,
        help_text=_('External branch location, ie: lp:snappy/15.04 or '
                    'git://github.com/ubuntu-core/snappy'))
    docs_namespace = models.CharField(
        max_length=120,
        help_text=_('Path alias we want to use for the docs, '
                    'ie "snappy/guides/15.04" or '
                    '"snappy/guides/latest", etc.'))
    index_doc = models.CharField(
        max_length=120,
        help_text=_('File name of doc to be used as index document, '
                    'ie "intro.md"'),
        blank=True)

class SEOExtension(TitleExtension):
    keywords = models.CharField(max_length=256)

extension_pool.register(SEOExtension)
