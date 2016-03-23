#!/bin/sh

mkdir -p /tmp/apidoc_sources/

# Archives to download packages from
export SERIES="vivid"

#### Apps/QML
## QtQML & QtQuick
./get_package.py qtdeclarative5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r development -s "Language Types" -N QtQml -i /tmp/apidoc_sources/usr/share/qt5/doc/qtqml/qtqml.index
python manage.py import_qdoc -p -t apps -l qml -r development -s "Graphical Interface" -n QtQuick -i /tmp/apidoc_sources/usr/share/qt5/doc/qtquick/qtquick.index

## QtMultimedia & QtAudioEngine
./get_package.py qtmultimedia5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r development -s "Multimedia" -n QtMultimedia -i /tmp/apidoc_sources/usr/share/qt5/doc/qtmultimedia/qtmultimedia.index

## QtSensors
./get_package.py qtsensors5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r development -s "Device and Sensors" -n QtSensors -i /tmp/apidoc_sources/usr/share/qt5/doc/qtsensors/qtsensors.index

## QtFeedback
./get_package.py qtfeedback5-doc-html
python manage.py import_qdoc -t apps -l qml -r development -s "Device and Sensors" -n QtFeedback -i /tmp/apidoc_sources/usr/share/qt5/doc/qtfeedback/qtfeedback.index

## QtLocation
./get_package.py qtlocation5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r development.1 -s "Platform Services" -i /tmp/apidoc_sources/usr/share/qt5/doc/qtlocation/qtlocation.index

## QtOrganizer
./get_package.py qtpim5-doc-html
python manage.py import_qdoc -t apps -l qml -r development -s "Platform Services" -i /tmp/apidoc_sources/usr/share/qt5/doc/qtorganizer/qtorganizer.index
python manage.py import_qdoc -t apps -l qml -r development -s "Platform Services" -i /tmp/apidoc_sources/usr/share/qt5/doc/qtcontacts/qtcontacts.index

## Ubuntu.Components
./get_package.py ubuntu-ui-toolkit-doc
python manage.py import_qdoc -Pp -t apps -l qml -r development -s "Graphical Interface" -n Ubuntu.Components -i /tmp/apidoc_sources/usr/share/ubuntu-ui-toolkit/doc/html/ubuntuuserinterfacetoolkit.index

## Ubuntu.OnlineAccounts
./get_package.py accounts-qml-module-doc
python manage.py import_qdoc -Pp -t apps -l qml -r development -s "Platform Services" -N Ubuntu.OnlineAccounts -i /tmp/apidoc_sources/usr/share/accounts-qml-module/doc/html/onlineaccounts-qml-api.index

## Ubuntu.Content
./get_package.py libcontent-hub-doc
gunzip -f /tmp/apidoc_sources/usr/share/doc/content-hub/qml/html/ubuntu-content-qml-api.index.gz
python manage.py import_qdoc -Pp -t apps -l qml -r development -s "Platform Services" -N Ubuntu.Content -i /tmp/apidoc_sources/usr/share/doc/content-hub/qml/html/ubuntu-content-qml-api.index

# U1db
./get_package.py libu1db-qt5-doc
python manage.py import_qdoc -p -t apps -l qml -r development -s "Platform Services" -N U1db -i /tmp/apidoc_sources/usr/share/u1db-qt/doc/html/u1db-qt.index

## Ubuntu.DownloadManager
./get_package.py libubuntu-download-manager-client-doc
gunzip -f /tmp/apidoc_sources/usr/share/doc/ubuntu-download-manager/qml/html/ubuntu-download-manager-qml-api.index.gz
python manage.py import_qdoc -Pp -t apps -l qml -r development -s "Platform Services" -N Ubuntu.DownloadManager -i /tmp/apidoc_sources/usr/share/doc/ubuntu-download-manager/qml/html/ubuntu-download-manager-qml-api.index

## Ubuntu.Web
./get_package.py qtdeclarative5-ubuntu-web-plugin-doc
gunzip -f /tmp/apidoc_sources/usr/share/doc/ubuntu-web/html/ubuntuweb.index.gz
python manage.py import_qdoc -Pp -t apps -l qml -r development -s "Graphical Interface" -N Ubuntu.Web -i /tmp/apidoc_sources/usr/share/doc/ubuntu-web/html/ubuntuweb.index

## Ubuntu.Connectivity
./get_package.py connectivity-doc
python manage.py import_qdoc -Pp -t apps -l qml -r development -s "Platform Services" -N Ubuntu.Connectivity -i /tmp/apidoc_sources/usr/share/doc/connectivity-api/qml/html/connectivity.index

#### Aps/HTML5
## UbuntuUI
./get_package.py ubuntu-html5-ui-toolkit-doc
python manage.py import_yuidoc -i -t apps -l html5 -r development -s "Graphical Interface" -d /tmp/apidoc_sources/usr/share/doc/ubuntu-html5-ui-toolkit-doc/data.json

## Platform Bindings
./get_package.py unity-webapps-qml-doc
## OnlineAccounts3
python manage.py import_yuidoc -t apps -l html5 -r development -s "Platform Services" -d /tmp/apidoc_sources/usr/share/unity-webapps-qml/doc/api/online-accounts/data.json
## AlarmAPI
python manage.py import_yuidoc -t apps -l html5 -r development -s "Platform Services" -d /tmp/apidoc_sources/usr/share/unity-webapps-qml/doc/api/alarm-api/data.json
## ContentHub
python manage.py import_yuidoc -t apps -l html5 -r development -s "Platform Services" -d /tmp/apidoc_sources/usr/share/unity-webapps-qml/doc/api/content-hub/data.json
## RuntimeAPI
python manage.py import_yuidoc -t apps -l html5 -r development -s "Platform Services" -d /tmp/apidoc_sources/usr/share/unity-webapps-qml/doc/api/runtime-api/data.json

#### Autopilot/Python
## Autopilot
./get_package.py python3-autopilot
find /tmp/apidoc_sources/usr/share/doc/python3-autopilot/json/ -name "*.gz" -print0 |xargs -0 gunzip
python manage.py import_sphinx -t autopilot -l python -r development -s ./api_docs/importers/autopilot_sections.py -i /tmp/apidoc_sources/usr/share/doc/python3-autopilot/json/objects.inv

./get_package.py ubuntu-ui-toolkit-autopilot
find /tmp/apidoc_sources/usr/share/doc/ubuntu-ui-toolkit-autopilot/json/ -name "*.gz" -print0 |xargs -0 gunzip
python manage.py import_sphinx -t autopilot -l python -r development -s ./api_docs/importers/autopilot_sections.py -i /tmp/apidoc_sources/usr/share/doc/ubuntu-ui-toolkit-autopilot/json/objects.inv

./get_package.py python3-scope-harness
find /tmp/apidoc_sources/usr/share/doc/python3-scope-harness/json/ -name "*.gz" -print0 |xargs -0 gunzip
python manage.py import_sphinx -t autopilot -l python -r development -s ./api_docs/importers/autopilot_sections.py -i /tmp/apidoc_sources/usr/share/doc/python3-scope-harness/json/objects.inv

#### Scopes/C++ 
## unity.scopes
./get_package.py libunity-scopes-doc
python manage.py import_doxygen -t scopes -l cpp -r development -s ./api_docs/importers/scope_sections.py -N unity.scopes -d /tmp/apidoc_sources/usr/share/doc/unity-scopes/

## Accounts
./get_package.py libaccounts-qt-doc
python manage.py import_doxygen -t scopes -l cpp -r development -s ./api_docs/importers/accounts_sections.py -n Accounts -d /tmp/apidoc_sources/usr/share/doc/libaccounts-qt/html/

## U1db
./get_package.py libu1db-qt5-doc
python manage.py import_qdoc -Pp -N U1db -t scopes -l cpp -r development -s "Platform Services" -i /tmp/apidoc_sources/usr/share/u1db-qt/doc/html/u1db-qt.index

#### Scopes/Javascript
SOURCE=http://ppa.launchpad.net/ubuntu-sdk-team/ppa/ubuntu ./get_package.py unity-js-scopes-doc
python manage.py import_yuidoc -t scopes -l js -r development -s "Platform Services" -d /tmp/apidoc_sources/usr/share/unity-js-scopes/doc/docbuild/data.json

rm -r /tmp/apidoc_sources/
