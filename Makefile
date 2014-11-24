#!/usr/bin/make
PYTHON := /usr/bin/env python

update-charm: collectstatic
	@echo "Updating charm"
	if [ $(DATABASE_URL) ]; then $(MAKE) initdb; fi

initdb: syncdb
	@echo "Initializing database"
	@python manage.py initdb --settings local_settings

syncdb: local_settings.py
	@echo "Syncing database"
	@python manage.py syncdb --noinput --migrate --settings local_settings

collectstatic: local_settings.py
	@echo "Collecting static files"
	@python manage.py collectstatic --settings local_settings

local_settings.py:
	SWIFT_AUTH_URL=${OS_AUTH_URL}
	SWIFT_TENANT_NAME=${OS_TENANT_NAME}
	SWIFT_REGION=${OS_REGION_NAME}
	SWIFT_USERNAME=${OS_USERNAME}
	SWIFT_PASSWORD=${OS_PASSWORD}
	SECRET_KEY=$(pwgen -s 50 1)
	DEBUG_MODE=False
	@./make_local_settings.sh


