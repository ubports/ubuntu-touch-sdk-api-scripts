from developer_portal.settings import LANGUAGE_CODE

from md_importer.models import ExternalDocsBranchImportDirective

import logging
logger = logging.getLogger('django')

DEFAULT_LANG = LANGUAGE_CODE
HOME_PAGE_URL = '/{}/'.format(DEFAULT_LANG)
SUPPORTED_ARTICLE_TYPES = ['.md', '.html']

# Instead of just using pymdownx.github, we go with these because of
# https://github.com/facelessuser/pymdown-extensions/issues/11
MARKDOWN_EXTENSIONS = [
    'markdown.extensions.footnotes',
    'markdown.extensions.tables',
    'markdown.extensions.toc',
    'pymdownx.magiclink',
    'pymdownx.betterem',
    'pymdownx.tilde',
    'pymdownx.githubemoji',
    'pymdownx.tasklist',
    'pymdownx.superfences',
]

model_info = ExternalDocsBranchImportDirective._meta
TEMPLATE_CHOICES = model_info.get_field('template').choices
DEFAULT_TEMPLATE = model_info.get_field('template').default
