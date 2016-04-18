from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


if settings.CMS_TEMPLATES:
    cms_templates = settings.CMS_TEMPLATES
else:
    cms_templates = (
        ('default.html', 'Default'),
    )


class ExternalDocsBranch(models.Model):
    origin = models.CharField(
        max_length=200,
        help_text=_('External branch location, ie: lp:snappy/15.04 or '
                    'https://github.com/ubuntu-core/snappy.git'))
    branch_name = models.CharField(
        max_length=200,
        help_text=_('For use with git branches, ie: "master" or "15.04" '
                    'or "1.x".'),
        blank=True)
    post_checkout_command = models.CharField(
        max_length=100,
        help_text=_('Command to run after checkout of the branch.'),
        blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.branch_name:
            return "{} - {}".format(self.origin, self.branch_name)
        return "{}".format(self.origin)

    class Meta:
        verbose_name = "external docs branch"
        verbose_name_plural = "external docs branches"


class ExternalDocsBranchImportDirective(models.Model):
    external_docs_branch = models.ForeignKey(ExternalDocsBranch)
    import_from = models.CharField(
        max_length=150,
        help_text=_('File or directory to import from the branch. '
                    'Ie: "docs/intro.md" (file) or '
                    '"docs" (complete directory), etc.'),
        blank=True)
    write_to = models.CharField(
        max_length=150,
        help_text=_('Article URL (for a specific file) or article namespace '
                    'for a directory or a set of files.'),
        blank=True)
    advertise = models.BooleanField(
        default=True,
        help_text=_('Should the imported articles be listed in the '
                    'navigation? Default: yes.'),
    )
    template = models.CharField(
        max_length=50,
        default=cms_templates[0][0],
        choices=cms_templates,
        help_text=_('Django CMS template to use for the imported articles. '
                    'Default: {}'.format(cms_templates[0][0])),
    )

    def __str__(self):
        return "{} -- {}".format(self.external_docs_branch,
                                 self.import_from)


class ImportedArticle(models.Model):
    url = models.CharField(
        max_length=300,
        help_text=_('URL of article, e.g. snappy/guides/security'),
    )
    branch = models.ForeignKey(ExternalDocsBranch)
    last_import = models.DateTimeField(
        _('Datetime'), help_text=_('Datetime of last import.'))

    def __str__(self):
        return '{} -- {} -- {}'.format(
            self.url, self.branch, self.last_import)
