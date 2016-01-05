# Use environment variables to configure database and swift access

import os
from developer_portal.settings import *

DEBUG=os.environ.get('DEBUG_MODE', False)=="True"
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split(',')

SECRET_KEY=os.environ.get('SECRET_KEY', '')

# Use original HOST header, so cn.developer.ubuntu.com redirects work
#USE_X_FORWARDED_HOST=True

# Database configs
import dj_database_url
DATABASES['default'].update(dj_database_url.config())

# SwiftStorage configs
INSTALLED_APPS.append('swiftstorage')

OS_USERNAME = os.environ.get('OS_USERNAME', '')
OS_PASSWORD = os.environ.get('OS_PASSWORD', '')
OS_AUTH_URL = os.environ.get('OS_AUTH_URL', '')
OS_REGION_NAME = os.environ.get('OS_REGION_NAME', '')
OS_TENANT_NAME = os.environ.get('OS_TENANT_NAME', '')

SWIFT_CONTAINER_NAME=os.environ.get('SWIFT_CONTAINER_NAME', 'devportal_uploaded')
DEFAULT_FILE_STORAGE = "swiftstorage.storage.SwiftStorage"

SWIFT_STATICCONTAINER_NAME=os.environ.get('SWIFT_STATICCONTAINER_NAME', 'devportal_static')
SWIFT_STATICFILE_PREFIX=''
STATICFILES_STORAGE = 'swiftstorage.storage.SwiftStaticStorage'

MEDIA_URL = os.environ.get('SWIFT_URL_BASE', '/media/') + "/%s/" % SWIFT_CONTAINER_NAME
STATIC_URL = os.environ.get('SWIFT_URL_BASE', '/static/') + "/%s/" % SWIFT_STATICCONTAINER_NAME
ASSETS_URL = os.environ.get('ASSETS_URL_BASE', '//assets.ubuntu.com/')

CACHE_MIDDLEWARE_SECONDS = 3600
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '../../logs/django_errors.log',
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
