from developer_portal.settings import LANGUAGE_CODE

DEFAULT_LANG = LANGUAGE_CODE
HOME_PAGE_URL = '/{}/'.format(DEFAULT_LANG)
SUPPORTED_ARTICLE_TYPES = ['.md', '.html']

# Instead of just using pymdownx.github, we go with these because of
# https://github.com/facelessuser/pymdown-extensions/issues/11
MARKDOWN_EXTENSIONS = [
    'markdown.extensions.tables',
    'pymdownx.magiclink',
    'pymdownx.betterem',
    'pymdownx.tilde',
    'pymdownx.githubemoji',
    'pymdownx.tasklist',
    'pymdownx.superfences',
]