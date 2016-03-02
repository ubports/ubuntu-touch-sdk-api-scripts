from django.core.management import call_command

import datetime
import pytz
import shutil
import tempfile

from md_importer.importer.repo import create_repo

from md_importer.models import (
    ExternalDocsBranchImportDirective,
    ImportedArticle,
)


def process_branch(branch):
    tempdir = tempfile.mkdtemp()
    repo = create_repo(tempdir, branch.origin, branch.branch_name,
                       branch.post_checkout_command)
    if repo.get() != 0:
        return False
    for directive in ExternalDocsBranchImportDirective.objects.filter(
            external_docs_branch=branch):
        repo.add_directive(directive.import_from,
                           directive.write_to,
                           directive.advertise)
    if not repo.execute_import_directives():
        return False
    if not repo.publish():
        return False
    timestamp = datetime.datetime.now(pytz.utc)

    # Update data in ImportedArticle table
    for page in repo.pages:
        if ImportedArticle.objects.filter(branch=branch, page=page).count():
            imported_article = ImportedArticle.objects.filter(
                branch=branch, page=page)[0]
            imported_article.last_import = datetime.datetime.now(pytz.utc)
            imported_article.save()
        else:
            ImportedArticle.objects.get_or_create(
                branch=branch,
                page=page,
                last_import=datetime.datetime.now(pytz.utc))

    # Remove old entries
    for imported_article in ImportedArticle.objects.filter(
            branch=branch, last_import__lt=timestamp):
        imported_article.page.delete()
        imported_article.delete()

    # The import is done, now let's clean up.
    imported_page_ids = [p.id for p in repo.pages
                         if p.changed_by in ['python-api', 'script']]
    ImportedArticle.objects.filter(
        branch=branch).filter(id__in=imported_page_ids).delete()
    shutil.rmtree(tempdir)

    # https://stackoverflow.com/questions/33284171/
    call_command('cms', 'fix-tree')
    return True
