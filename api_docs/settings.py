import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

SITE_ID = 1

CSRF_COOKIE_SECURE = False
SECRET_KEY = 'we3w67a1=2e384asi&f_fcp8meje#)n@lyoys21izkwo)%eknh'
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '.developer.ubuntu.com']


INSTALLED_APPS = [
    'api_docs',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MIDDLEWARE_CLASSES = []
