# -*- coding: utf-8 -*-
"""
Django settings for developer_portal project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
from gettext import gettext

ADMIN_GROUP = 'ubuntudeveloperportal'
EDITOR_GROUP = 'ubuntu-website-editors'

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

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Allow login from Ubuntu SSO
    'django_openid_auth',

    'mptt', #utilities for implementing a modified pre-order traversal tree
    'menus', #helper for model independent hierarchical website navigation
    'south', #intelligent schema and data migrations
    'sekizai', #for javascript and css management
    'reversion', #content versioning
    'django_pygments',
    'django_comments',
    'tagging',

    'ckeditor',
    'djangocms_text_ckeditor',

    'cms', #django CMS itself
    'djangocms_link',
    'djangocms_picture',
    'djangocms_video',
    'djangocms_snippet',

    'cmsplugin_zinnia',
    'zinnia',
    'zinnia_ckeditor',

    'developer_portal',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',

    'sekizai.context_processors.sekizai',
    'cms.context_processors.cms_settings',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, "templates"),
)

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

# 
# Django CMS specific settings
# 
CMS_PERMISSION = True

CMS_CACHE_DURATIONS = {
    'menus': 0,
}

CMS_TEMPLATES = (
    ('default.html', 'Default'),
    ('landing_page.html', 'Landing Page'),
    ('no_subnav.html', 'Without Subnav'),
    ('with_hero.html', 'With Hero'),
)

LANGUAGES = [
    ('en', 'English'),
    ('zh-cn', u'简体中文'),
    ('es', u'Español'),
]

CMS_LANGUAGES = {
    1: [
        {
            'code': 'en',
            'name': gettext('English'),
            'public': True,
            'hide_untranslated': True,
            'redirect_on_fallback': False,
        },
        {
            'code': 'zh',
            'name': gettext('Chinese'),
            'fallbacks': ['en'],
            'hide_untranslated': True,
            'redirect_on_fallback': False,
            'public': True,
        },
        {
            'code': 'es',
            'name': gettext('Spanish'),
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

CKEDITOR_UPLOAD_PATH = "media/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# OPENID Related settings
OPENID_STRICT_USERNAMES = True
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
        'name': gettext("Page content"),
        'default_plugins': [
            {
                'plugin_type': 'TextPlugin',
                'values': {
                    'body':'<p>Add content here...</p>',
                },
            },
        ],
    },
}
