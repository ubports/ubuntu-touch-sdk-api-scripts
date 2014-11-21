#!/bin/bash

# Common variables used in setting up the service

SWIFT_AUTH_URL=${OS_AUTH_URL}
SWIFT_TENANT_NAME=${OS_TENANT_NAME}
SWIFT_REGION=${OS_REGION}
SWIFT_USERNAME=${OS_USERNAME}
SWIFT_PASSWORD=${OS_PASSWORD}
SWIFT_CONTAINER=${OS_CONTAINER}

LOCAL_SETTINGS_FILE=./local_settings.py


echo "Creating local settings in ${LOCAL_SETTINGS_FILE}"
SECRET_KEY=$(pwgen -s 50 1)
cat > ${LOCAL_SETTINGS_FILE} <<EOF
# Regularly update Summit

from developer_portal.settings import *

DEBUG=${DEBUG_MODE}

SECRET_KEY='${SECRET_KEY}'

# Database configs
import dj_database_url
DATABASES['default'].update(dj_database_url.config())

# SwiftStorage configs
INSTALLED_APPS.append('swiftstorage')

OS_USERNAME = "${SWIFT_USERNAME}"
OS_PASSWORD = "${SWIFT_PASSWORD}"
OS_AUTH_URL = "${SWIFT_AUTH_URL}"
OS_REGION_NAME = "${SWIFT_REGION}"
OS_TENANT_NAME = "${SWIFT_TENANT_NAME}"

SWIFT_CONTAINER_NAME='devportal_uploaded'
DEFAULT_FILE_STORAGE = "swiftstorage.storage.SwiftStorage"

SWIFT_STATICCONTAINER_NAME='devportal_static'
SWIFT_STATICFILE_PREFIX=''
STATICFILES_STORAGE = 'swiftstorage.storage.SwiftStaticStorage'

MEDIA_URL = "https://swift.canonistack.canonical.com/v1/AUTH_c70ce6d1363e4692b1d4fde91eaa3b4b/%s/" % SWIFT_CONTAINER_NAME
STATIC_URL = "https://swift.canonistack.canonical.com/v1/AUTH_c70ce6d1363e4692b1d4fde91eaa3b4b/%s/" % SWIFT_STATICCONTAINER_NAME

EOF
