from django.db import models
from django.utils.translation import ugettext_lazy as _

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
    branch_origin = models.CharField(
        max_length=200,
        help_text=_('External branch location, ie: lp:snappy/15.04 or '
                    'https://github.com/ubuntu-core/snappy.git'))
    post_checkout_command = models.CharField(
        max_length=100,
        help_text=_('Command to run after checkout of the branch.'),
        blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "external docs branch"
        verbose_name_plural = "external docs branches"


class ExternalDocsBranchImportDirective(models.Model):
    external_docs_branch = models.ForeignKey(ExternalDocsBranch)
    import_from = models.CharField(
        max_length=150,
        help_text=_('File or directory to import from the branch. '
                    'Feel free to use globs, ie: "docs/intro.md" (file) or '
                    '"docs" (complete directory), '
                    '"docs/a*" (some select files), etc.'))
    write_to = models.CharField(
        max_length=150,
        help_text=_('Article URL (for a specific file) or article namespace '
                    'for a directory or a set of files.'))


class SEOExtension(TitleExtension):
    keywords = models.CharField(max_length=256)

extension_pool.register(SEOExtension)
