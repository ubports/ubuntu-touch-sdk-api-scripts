#!/bin/sh

mkdir -p /tmp/apidoc_sources/

# Archives to download packages from
export SERIES="utopic"

#### Apps/QML
## QtQML & QtQuick
./get_package.sh qtdeclarative5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r sdk-14.10 -s "Language Types" -N QtQml -i /tmp/apidoc_sources/usr/share/qt5/doc/qtqml/qtqml.index
python manage.py import_qdoc -p -t apps -l qml -r sdk-14.10 -s "Graphical Interface" -n QtQuick -i /tmp/apidoc_sources/usr/share/qt5/doc/qtquick/qtquick.index

## QtMultimedia & QtAudioEngine
./get_package.sh qtmultimedia5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r sdk-14.10 -s "Multimedia" -n QtMultimedia -i /tmp/apidoc_sources/usr/share/qt5/doc/qtmultimedia/qtmultimedia.index

## QtSensors
./get_package.sh qtsensors5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r sdk-14.10 -s "Device and Sensors" -n QtSensors -i /tmp/apidoc_sources/usr/share/qt5/doc/qtsensors/qtsensors.index

#python manage.py import_qdoc -t apps -l qml -r sdk-14.10 -s "Device and Sensors" -n QtFeedback -i ~/projects/Ubuntu/sdk/qtfeedback-opensource-src/doc/html/qtfeedback.index

## QtLocation
./get_package.sh qtlocation5-doc-html
python manage.py import_qdoc -p -t apps -l qml -r sdk-14.10 -s "Platform Services" -i /tmp/apidoc_sources/usr/share/qt5/doc/qtlocation/qtlocation.index

#(Need to poke Mirv)python manage.py import_qdoc -t apps -l qml -r sdk-14.10 -s "Platform Services" -i ~/projects/Ubuntu/api-website/qtpim-opensource-src/doc/html/qtpim.index

## Ubuntu.Components
./get_package.sh ubuntu-ui-toolkit-doc
python manage.py import_qdoc -Pp -t apps -l qml -r sdk-14.10 -s "Graphical Interface" -n Ubuntu.Components -i /tmp/apidoc_sources/usr/share/ubuntu-ui-toolkit/doc/html/ubuntuuserinterfacetoolkit.index

## Ubuntu.OnlineAccounts
./get_package.sh accounts-qml-module-doc
python manage.py import_qdoc -Pp -t apps -l qml -r sdk-14.10 -s "Platform Services" -N Ubuntu.OnlineAccounts -i /tmp/apidoc_sources/usr/share/accounts-qml-module/doc/html/onlineaccounts-qml-api.index

## Ubuntu.Content
./get_package.sh libcontent-hub-doc
gunzip -f /tmp/apidoc_sources/usr/share/doc/content-hub/qml/html/ubuntu-content-qml-api.index.gz
python manage.py import_qdoc -Pp -t apps -l qml -r sdk-14.10 -s "Platform Services" -N Ubuntu.Content -i /tmp/apidoc_sources/usr/share/doc/content-hub/qml/html/ubuntu-content-qml-api.index

#???
python manage.py import_qdoc -Pp -t apps -l qml -r sdk-14.10 -s "Platform Services" -N U1db -i /tmp/apidoc_sources/usr/share/u1db-qt/doc/html/u1db-qt.index

## Ubuntu.DownloadManager
./get_package.sh libubuntu-download-manager-client-doc
gunzip -f /tmp/apidoc_sources/usr/share/doc/ubuntu-download-manager/qml/html/ubuntu-download-manager-qml-api.index.gz
python manage.py import_qdoc -Pp -t apps -l qml -r sdk-14.10 -s "Platform Services" -N Ubuntu.DownloadManager -i /tmp/apidoc_sources/usr/share/doc/ubuntu-download-manager/qml/html/ubuntu-download-manager-qml-api.index

## Ubuntu.Web
./get_package.sh qtdeclarative5-ubuntu-web-plugin-doc
gunzip -f /tmp/apidoc_sources/usr/share/doc/ubuntu-web/html/ubuntuweb.index.gz
python manage.py import_qdoc -Pp -t apps -l qml -r sdk-14.10 -s "Graphical Interface" -N Ubuntu.Web -i /tmp/apidoc_sources/usr/share/doc/ubuntu-web/html/ubuntuweb.index

#### Aps/HTML5
#python manage.py import_yuidoc -i -t apps -l html5 -r sdk-14.10 -s "Graphical Interface" -d /home/mhall/projects/Ubuntu/sdk/ubuntu-html5-theme/0.1/ambiance/js/build/data.json
#python manage.py import_cordova -t apps -l html5 -r sdk-14.10 -i /home/mhall/projects/Ubuntu/sdk/cordova-docs-pkg/edge/index.json
#python manage.py import_yuidoc -t apps -l html5 -r sdk-14.10 -s "Platform Services" -d /home/mhall/projects/Ubuntu/sdk/unity-webapps-qml/src/Ubuntu/UnityWebApps/bindings/online-accounts/client/docsbuild/data.json
#python manage.py import_yuidoc -t apps -l html5 -r sdk-14.10 -s "Platform Services" -d /home/mhall/projects/Ubuntu/sdk/unity-webapps-qml/src/Ubuntu/UnityWebApps/bindings/alarm-api/client/docsbuild/data.json
#python manage.py import_yuidoc -t apps -l html5 -r sdk-14.10 -s "Platform Services" -d /home/mhall/projects/Ubuntu/sdk/unity-webapps-qml/src/Ubuntu/UnityWebApps/bindings/content-hub/client/docsbuild/data.json
#python manage.py import_yuidoc -t apps -l html5 -r sdk-14.10 -s "Platform Services" -d /home/mhall/projects/Ubuntu/sdk/unity-webapps-qml/src/Ubuntu/UnityWebApps/bindings/runtime-api/client/docsbuild/data.json

#### Autopilot/Python
## Autopilot
SERIES=vivid ./get_package.sh python3-autopilot
find /tmp/apidoc_sources/usr/share/doc/python3-autopilot/json/ -name "*.gz" -print0 |xargs -0 gunzip
python manage.py import_sphinx -t autopilot -l python -r 1.5.0 -s ./api_docs/importers/autopilot_sections.py -i /tmp/apidoc_sources/usr/share/doc/python3-autopilot/json/objects.inv

#### Scopes/C++ 
## unity.scopes
./get_package.sh libunity-scopes-doc
python manage.py import_doxygen -t scopes -l cpp -r sdk-14.10 -s ./api_docs/importers/scope_sections.py -N unity.scopes -d /tmp/apidoc_sources/usr/share/doc/unity-scopes/

## Accounts
./get_package.sh libaccounts-qt-doc
python manage.py import_doxygen -t scopes -l cpp -r sdk-14.10 -s ./api_docs/importers/accounts_sections.py -n Accounts -d /tmp/apidoc_sources/usr/share/doc/libaccounts-qt/html/

## U1db
./get_package.sh libu1db-qt5-doc
python manage.py import_qdoc -Pp -N U1db -t scopes -l cpp -r sdk-14.10 -s "Platform Services" -i /tmp/apidoc_sources/usr/share/u1db-qt/doc/html/u1db-qt.index

#rm -r /tmp/apidoc_sources/
