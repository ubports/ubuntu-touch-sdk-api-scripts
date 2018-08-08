#!/bin/bash

# Script to orchestrate the download and build of the Ubuntu Touch SDK API docs
# Once finished, the built rst can be found in ./rst

# This script should only be run on an Ubuntu 16.04 machine that you don't mind
# being littered with new packages (think container)

apt update
apt -y install python-pip bzr pandoc python-virtualenv make --no-install-recommends
pip install -r requirements.txt
python manage.py migrate
python manage.py init_apidocs

./update_apidocs.sh

python ./manage.py export_docs

cp -r ./template/* /tmp/sdk/

pushd /tmp/sdk

python -m virtualenv ~/ubportsdocsenv/ --python=python2
. ~/ubportsdocsenv/bin/activate
pip install -r requirements.txt --upgrade

make html SPHINXOPTS="-j `getconf _NPROCESSORS_ONLN`"

deactivate
popd

cp -r /tmp/sdk/_build/html ./built_docs/

rm -r /tmp/sdk
