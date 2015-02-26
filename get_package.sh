#!/bin/sh

PACKAGE=$1
if [ "X$1" = "X" ]; then
    echo "You must supply a package name"
    exit 1
fi
if [ "X$SERIES" = "X" ]; then
    echo "No SERIES env, defaulting to utopic"
    SERIES="utopic"
fi

REV=$(rmadison -s ${SERIES} ${PACKAGE} |awk -e "{ print \$3; }")
if [ "X${REV}" = "X" ]; then
    echo "No revision found for ${PACKAGE} on ${SERIES}"
    exit 2
fi
echo "Fetching ${PACKAGE}_${REV}"
if [ ! -d /tmp/apidoc_sources ]; then
    mkdir /tmp/apidoc_sources
fi

if [ -e /tmp/apidoc_sources/${PACKAGE}_${REV}_all.deb ]; then
    rm /tmp/apidoc_sources/${PACKAGE}_${REV}_all.deb
fi

wget -P /tmp/apidoc_sources/ -nc https://launchpad.net/ubuntu/+archive/primary/+files/${PACKAGE}_${REV}_all.deb
dpkg-deb --extract /tmp/apidoc_sources/${PACKAGE}_${REV}_all.deb /tmp/apidoc_sources/
