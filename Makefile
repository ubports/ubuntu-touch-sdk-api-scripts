#!/usr/bin/make
PYTHON := /usr/bin/env python
SOURCE_DIR := $(PWD)

update-instance:
	@echo "Nothing to do for the app";
	
update-common:
	@echo "Updating database"
	if [ $(DATABASE_URL) ]; then $(MAKE) initdb; fi
	if [ $(DATABASE_URL) ]; then $(MAKE) crontab; fi
	if [ $(DATABASE_URL) ]; then $(MAKE) swift-perms; fi

swift-perms:
	@echo "Setting up Swift bucket permissions"
	@if [ "${SWIFT_CONTAINER_NAME}" = "" ]; then echo "Using default upload container"; http_proxy="${swift_proxy}" https_proxy="${swift_proxy}" swift post --read-acl '.r:*' devportal_uploaded; else http_proxy="${swift_proxy}" https_proxy="${swift_proxy}" swift post --read-acl '.r:*' $(SWIFT_CONTAINER_NAME); fi
	@if [ "${SWIFT_STATICCONTAINER_NAME}" = "" ]; then echo "Using default static container"; http_proxy="${swift_proxy}" https_proxy="${swift_proxy}" swift post --read-acl '.r:*' devportal_static; else http_proxy="${swift_proxy}" https_proxy="${swift_proxy}" swift post --read-acl '.r:*' $(SWIFT_STATICCONTAINER_NAME); fi

update-apidocs:
	if [ $(DATABASE_URL) ]; then DJANGO_SETTINGS_MODULE=charm_settings ./update_apidocs.sh > ${PWD}/../../logs/update_apidocs.log 2>${PWD}/../../logs/update_apidocs_errors.log; fi

crontab:
	@echo '# Crontab generated by lp:developer-ubuntu-com and wsgi-app charm' > crontab
	@echo OS_USERNAME=\"${OS_USERNAME}\" >> crontab
	@echo OS_TENANT_NAME=\"${OS_TENANT_NAME}\" >> crontab
	@echo DATABASE_URL=\"${DATABASE_URL}\" >> crontab
	@echo OS_AUTH_URL=\"${OS_AUTH_URL}\" >> crontab
	@echo DEBUG_MODE=\"${DEBUG_MODE}\" >> crontab
	@echo OS_REGION_NAME=\"${OS_REGION_NAME}\" >> crontab
	@echo OS_PASSWORD=\"${OS_PASSWORD}\" >> crontab
	@echo SECRET_KEY=\"${SECRET_KEY}\" >> crontab
	@echo SWIFT_URL_BASE=\"${SWIFT_URL_BASE}\" >> crontab
	@echo DJANGO_SETTINGS_MODULE=\"charm_settings\" >> crontab
	@echo internal_proxy=\"${internal_proxy}\" >> crontab
	@echo "0 4 * * * cd ${PWD}; ./update_apidocs.sh > ${PWD}/../../logs/update_apidocs.log 2>${PWD}/../../logs/update_apidocs_errors.log" >> crontab
	@echo "15 4 * * * cd ${PWD}; ${PYTHON} manage.py update-gadget-snaps > ${PWD}/../../logs/update_gadgetsnaps.log 2>${PWD}/../../logs/update_gadgetsnaps_errors.log" >> crontab
	@echo "15 */2 * * * cd ${PWD}; ${PYTHON} manage.py import-external-docs-branches > ${PWD}/../../logs/import-external-docs-branches.log 2>${PWD}/../../logs/import-external-docs-branches_errors.log" >> crontab
	@crontab ./crontab
	@rm ./crontab

initdb: syncdb
	@echo "Initializing database"
	@python manage.py initdb --settings charm_settings
	@python manage.py init_apidocs --settings charm_settings

syncdb:
	@echo "Syncing database"
	@python manage.py syncdb --noinput --migrate --settings charm_settings

collectstatic: collectstatic.done
collectstatic.done:
	@echo "Collecting static files"
	@http_proxy="${swift_proxy}" https_proxy="${swift_proxy}" python manage.py collectstatic -v 0 --noinput --settings charm_settings 2>/dev/null
	@touch collectstatic.done

collectstatic.debug:
	@echo "Debugging output from collectstatic"
	@http_proxy="${swift_proxy}" https_proxy="${swift_proxy}" python manage.py collectstatic -v 1 --noinput --settings charm_settings

update-pip-cache:
	@echo "Updating pip-cache"
	rm -rf pip-cache
	bzr branch lp:~developer-ubuntu-com-dev/developer-ubuntu-com/dependencies pip-cache
	pip install --exists-action=w --download pip-cache/ -r requirements.txt
	bzr add pip-cache/* 
	bzr commit pip-cache/ -m 'automatically updated devportal requirements'
	bzr push --directory pip-cache lp:~developer-ubuntu-com-dev/developer-ubuntu-com/dependencies
	bzr revno pip-cache > pip-cache-revno.txt
	rm -rf pip-cache
	@echo "** Remember to commit pip-cache-revno.txt"

pip-cache:
	@echo "Downloading pip-cache"
	bzr branch -r `cat pip-cache-revno.txt` lp:~developer-ubuntu-com-dev/developer-ubuntu-com/dependencies pip-cache

translations:
	@echo "Updating translations"
	@python manage.py translations

tarball: pip-cache
	@echo "Creating tarball in ../developer_portal.tar.gz"
	cd ..; tar -C $(SOURCE_DIR) --exclude-vcs --exclude=./media --exclude=./env --exclude=./db.sqlite3 --exclude=*.pyc -czf developer_portal.tar.gz .
