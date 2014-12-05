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

collectstatic: collectstatic.done
collectstatic.done: local_settings.py
	@echo "Collecting static files"
	@python manage.py collectstatic --noinput --settings local_settings
	@touch collectstatic.done

local_settings.py:
	SECRET_KEY=$(pwgen -s 50 1)
	DEBUG_MODE=${DEBUG_MODE}
	@./make_local_settings.sh

build-pip-cache:
	-rm -rf pip-cache
	bzr branch lp:~mhall119/developer-ubuntu-com/dependencies pip-cache
	pip install --exists-action=w --download pip-cache/ -r requirements.txt
	bzr commit pip-cache/ -m 'automatically updated devportal requirements'
	bzr push --directory pip-cache lp:~mhall119/developer-ubuntu-com/dependencies
	bzr revno pip-cache > pip-cache-revno.txt
	rm -rf pip-cache
	@echo "** Remember to commit pip-cache-revno.txt"
