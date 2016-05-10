# -*- coding: utf-8 -*-
"""
Django settings for developer_portal project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from django.utils.translation import ugettext_lazy as _

ADMIN_GROUP = 'ubuntudeveloperportal'
EDITOR_GROUP = 'ubuntudeveloperportal-editors'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'we3w67a1=2e384asi&f_fcp8meje#)n@lyoys21izkwo)%eknh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'developer.ubuntu.com']


# Application definition

INSTALLED_APPS = [
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Allow login from Ubuntu SSO
    'django_openid_auth',

    'menus', #helper for model independent hierarchical website navigation
    'sekizai', #for javascript and css management
    'reversion', #content versioning
    'django_pygments',
    'django_comments',
    'tagging',
    'template_debug',

    'ckeditor',
    'djangocms_text_ckeditor',

    'cms', #django CMS itself
    'djangocms_inherit',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_video',
    'djangocms_snippet',
    'treebeard',

    'cmsplugin_zinnia',
    'zinnia',
    'zinnia_ckeditor',

    'developer_portal',

    'webapp_creator',

    'store_data',

    'api_docs',

    'md_importer',
]

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',

    # Replace standard session middleware with one that will strip
    # sessionid from the Cookie on anonymous sessions
    #
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'developer_portal.middleware.CacheFriendlySessionMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',

    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',

)
#CACHE_MIDDLEWARE_SECONDS = 3600
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, "templates"),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.core.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',

                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    }
]


ROOT_URLCONF = 'developer_portal.urls'

WSGI_APPLICATION = 'developer_portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH, "static")

MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")
MEDIA_URL = '/media/'

ASSETS_URL = '//assets.ubuntu.com/'

# Django CMS specific settings
#
CMS_PERMISSION = True

CMS_CACHE_DURATIONS = {
    'menus': 0,
    'content': 60,
    'permissions': 3600,
}

CMS_TEMPLATES = (
    ('default.html', 'Default'),
    ('landing_page.html', 'Landing Page'),
    ('no_subnav.html', 'Without Subnav'),
    ('with_hero.html', 'With Hero'),
    ('snappy_hero_tour.html', 'Snappy Hero Tour'),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'locale'),
)

LANGUAGES = [
    ('en', _('English')),
    ('zh-cn', _('Simplified Chinese')),
]

CMS_LANGUAGES = {
    1: [
        {
            'code': 'en',
            'name': _('English'),
            'public': True,
            'hide_untranslated': True,
            'redirect_on_fallback': False,
        },
        {
            'code': 'zh-cn',
            'name': _('Simplified Chinese'),
            'fallbacks': ['en'],
            'hide_untranslated': True,
            'redirect_on_fallback': False,
            'public': True,
        },
        {
            'code': 'es',
            'name': _('Spanish'),
            'fallbacks': ['en'],
            'hide_untranslated': False,
            'redirect_on_fallback': False,
            'public': True,
        },
    ],
    'default': {
        'fallbacks': ['en'],
        'redirect_on_fallback':False,
        'public': False,
        'hide_untranslated': False,
    }
}

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# OPENID Related settings
OPENID_STRICT_USERNAMES = False
OPENID_FOLLOW_RENAMES = True
OPENID_SREG_REQUIRED_FIELDS = ['email']
OPENID_CREATE_USERS = True
OPENID_REUSE_USERS = False
OPENID_UPDATE_DETAILS_FROM_SREG = True
OPENID_SSO_SERVER_URL = 'https://login.ubuntu.com/'
OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO = True

# Tell django.contrib.auth to use the OpenID signin URLs.
LOGIN_URL = '/openid/login'
LOGIN_REDIRECT_URL = '/'

# Django 1.6 uses a JSON serializer by default, which breaks
# django_openid_auth, so force it to use the old default
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

CMS_PLACEHOLDER_CONF = {
    'page_content': {
        'name': _("Page content"),
        'default_plugins': [
            {
                'plugin_type': 'TextPlugin',
                'values': {
                    # Translators: this is the default text that will be shown
                    # to editors when editing a page. You can use some HTML,
                    # but don't go wild :)
                    'body': _('<p>Add content here...</p>'),
                },
            },
        ],
    },
}

CKEDITOR_UPLOAD_PATH = "media/"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = 'dummy'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
    },
    'zinnia-content': {
        'toolbar_Zinnia': [
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],
            ['Undo', 'Redo'],
            ['Scayt'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Source'],
            ['Maximize'],
            '/',
            ['Bold', 'Italic', 'Underline', 'Strike',
             'Subscript', 'Superscript', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-',
             'Outdent', 'Indent', '-', 'Blockquote'],
            ['Styles', 'Format'],
        ],
        'toolbar': 'Zinnia',
    },
}

# Allow iframes in ckeditor
TEXT_ADDITIONAL_TAGS = ('iframe',)
TEXT_ADDITIONAL_ATTRIBUTES = ('scrolling', 'allowfullscreen', 'frameborder')

CMSPLUGIN_ZINNIA_APP_URLS = ['developer_portal.blog.urls']

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),

    #'PAGINATE_BY': 10,
}

MIGRATION_MODULES = {
    'cms': 'cms.migrations',
    'cmsplugin_zinnia': 'cmsplugin_zinnia.migrations',
    'djangocms_link': 'djangocms_link.migrations',
    'djangocms_picture': 'djangocms_picture.migrations',
    'djangocms_snippet': 'djangocms_snippet.migrations',
    'djangocms_text_ckeditor': 'djangocms_text_ckeditor.migrations',
    'djangocms_video': 'djangocms_video.migrations',
    'django_comments': 'django_comments.migrations',
    'menus': 'menus.migrations',
    'rest_framework.authtoken': 'rest_framework.authtoken.migrations',
    'reversion': 'reversion.migrations',
    'tagging': 'tagging.migrations',
    'taggit': 'taggit.migrations',
    'zinnia': 'zinnia.migrations',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': './error.log',
            'formatter': 'normal',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['errors'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
