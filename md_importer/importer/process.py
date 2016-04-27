import datetime
import pytz
import shutil
import tempfile

from django.core.management import call_command

from md_importer.importer import logger
from md_importer.importer.publish import find_page
from md_importer.importer.repo import Repo
from md_importer.models import (
    ExternalDocsBranchImportDirective,
    ImportedArticle,
)


def process_branch(branch):
    tempdir = tempfile.mkdtemp()
    repo = Repo(tempdir, branch.origin, branch.branch_name,
                branch.post_checkout_command)
    if repo.get() != 0:
        return None
    for directive in ExternalDocsBranchImportDirective.objects.filter(
            external_docs_branch=branch):
        repo.add_directive(directive.import_from,
                           directive.write_to,
                           directive.advertise,
                           directive.template)
    if not repo.execute_import_directives():
        return None
    if not repo.publish():
        return None
    timestamp = datetime.datetime.now(pytz.utc)

    # Update data in ImportedArticle table
    for page in repo.pages:
        url = page.get_absolute_url()
        if ImportedArticle.objects.filter(branch=branch, url=url).count():
            imported_article = ImportedArticle.objects.filter(
                branch=branch, url=url)[0]
            imported_article.last_import = timestamp
            imported_article.save()
        else:
            imported_article, created = ImportedArticle.objects.get_or_create(
                branch=branch,
                url=url,
                last_import=timestamp)

    # Remove old entries
    for imported_article in ImportedArticle.objects.filter(
            branch=branch, last_import__lt=timestamp):
        page = find_page(imported_article.url)
        if not page:
            logger.error('Page {} not found for deletion.'.format(url))
        else:
            page.delete()
            imported_article.delete()

    # The import is done, now let's clean up.
    imported_page_ids = [p.id for p in repo.pages
                         if p.changed_by in ['python-api', 'script']]
    ImportedArticle.objects.filter(
        branch=branch).filter(id__in=imported_page_ids).delete()
    shutil.rmtree(tempdir)

    return repo
