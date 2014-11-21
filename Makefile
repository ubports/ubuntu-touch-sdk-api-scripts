#!/usr/bin/make
PYTHON := /usr/bin/env python

update-charm: initdb collectstatic


initdb: syncdb
	@python manage.py initdb --settings local_settings

syncdb: local_settings.py
	@python manage.py syncdb --noinput --migrate --settings local_settings

collectstatic: local_settings.py
	@python manage.py collectstatic --settings local_settings

local_settings.py:
	SWIFT_AUTH_URL=${OS_AUTH_URL}
	SWIFT_TENANT_NAME=${OS_TENANT_NAME}
	SWIFT_REGION=${OS_REGION}
	SWIFT_USERNAME=${OS_USERNAME}
	SWIFT_PASSWORD=${OS_PASSWORD}
	SWIFT_CONTAINER=${OS_CONTAINER}
	SECRET_KEY=$(pwgen -s 50 1)
	DEBUG_MODE=False
	@./make_local_settings.sh


