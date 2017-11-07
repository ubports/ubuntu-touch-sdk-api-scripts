# Scripts to generate the Ubuntu Touch SDK API Docs

This is a fork of the scripts behind the old api docs located at
[developer.ubuntu.com](https://code.launchpad.net/developer-ubuntu-com).
It currently is a django app, but wouldn't need to be if time
is taken to convert it. But in the interest of getting the docs
outside of developer.ubuntu.com this step has not been taken yet.

## Usage

* Install [vagrant](http://vagrantup.com/)
* Start vagrant
    * Run: `vagrant up`
* SSH into the vagrant VM
    * Run: `vagrant ssh`
* Import the docs into the database
    * Run: `./update_apidocs.sh`
* Export the docs to rst
    * Run `python ./manage.py export_docs`
    * The resulting docs will be located in `/tmp/sdk`
