#!/bin/sh

export http_proxy=${internal_proxy}
export https_proxy=${internal_proxy}

PACKAGE=$1
if [ "X$1" = "X" ]; then
    echo "You must supply a package name"
    exit 1
fi
if [ "X$DISTRO" = "X" ]; then
    echo "No DISTRO env, defaulting to ubuntu"
    DISTRO="ubuntu"
fi

if [ "X$SERIES" = "X" ]; then
    echo "No SERIES env, defaulting to utopic"
    SERIES="utopic"
fi

if [ "X$ARCH" = "X" ]; then
    echo "No ARCH env, defaulting to all"
    ARCH="all"
fi

REV=$(./rmadison -s ${SERIES} ${PACKAGE} |grep ${ARCH} |awk -e "{ print \$3; }")
if [ "X${REV}" = "X" ]; then
    echo "No revision found for ${PACKAGE} in ${SERIES} for ${ARCH}"
    exit 2
fi
echo "Fetching ${PACKAGE}_${REV}_${ARCH}"
if [ ! -d /tmp/apidoc_sources ]; then
    mkdir /tmp/apidoc_sources
fi

if [ -e /tmp/apidoc_sources/${PACKAGE}_${REV}_${ARCH}.deb ]; then
    rm /tmp/apidoc_sources/${PACKAGE}_${REV}_${ARCH}.deb
fi

wget -P /tmp/apidoc_sources/ -nc "https://launchpad.net/${DISTRO}/+archive/primary/+files/${PACKAGE}_${REV}_${ARCH}.deb"
dpkg-deb --extract /tmp/apidoc_sources/${PACKAGE}_${REV}_${ARCH}.deb /tmp/apidoc_sources/
