#!/usr/bin/python

import subprocess
import glob
import sys
import os

ARCH = os.getenv('ARCH', "all")
DISTRO = os.getenv('DISTRO', "ubuntu")
RELEASE = os.getenv('SERIES', "vivid")
APT_SOURCE = os.getenv('SOURCE')
PACKAGES = sys.argv[1:]

TMP_DIR = os.path.expanduser("~/tmp/")
UNPACKED_USRSHARE_DIR = os.path.join(TMP_DIR, "1/usr/share")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", default="/tmp/apidoc_sources/")

APT_LINES = [ "deb http://ppa.launchpad.net/ci-train-ppa-service/stable-phone-overlay/ubuntu %s main" % RELEASE,
              "deb http://archive.ubuntu.com/ubuntu %s main" % RELEASE,
              "deb http://archive.ubuntu.com/ubuntu %s universe" % RELEASE ]
if (APT_SOURCE):
    APT_LINES.append("deb %s %s main" % (APT_SOURCE, RELEASE))

PARTIAL_DIR = os.path.join(TMP_DIR, "lists/partial")
ETC_APT_DIR = os.path.join(TMP_DIR, "etc/apt")
CACHE_APT_DIR = os.path.join(TMP_DIR, "var/cache/apt")
VAR_DPKG_DIR = os.path.join(TMP_DIR, "var/lib/dpkg/")
DPKG_STATUS = os.path.join(VAR_DPKG_DIR, "status")
TRUSTED_DIR = os.path.join(ETC_APT_DIR, "trusted.gpg.d")
PREFERENCES_DIR = os.path.join(ETC_APT_DIR, "preferences.d")
SOURCES_LIST_FILE = os.path.join(ETC_APT_DIR, "sources.list")
LOCAL_KEYRING = os.path.join(os.path.abspath(os.path.dirname(__file__)), "keyring.gpg")

def safe_remove(what, contents_only=False):
    if os.path.exists(what):
        if os.path.isdir(what):
            if contents_only or subprocess.call(["rm", "-rf", what]) != 0:
                os.system("rm -rf %s/*" % what)
        if os.path.isfile(what):
            os.remove(what)
            
def safe_mkdirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_sources_list():
    safe_remove(SOURCES_LIST_FILE)
    f = open(SOURCES_LIST_FILE, "a")
    f.write("\n".join(APT_LINES))
    f.close()

def call_with_apt_args(s):
    apt_args = "-o", "Dir::State::lists=%s" % os.path.join(TMP_DIR, "lists"), \
               "-o", "Dir::Etc=%s" % ETC_APT_DIR, \
               "-o", "Dir::State=%s" % TMP_DIR, \
               "-o", "Dir::State::status=%s" % DPKG_STATUS, \
               "-o", "Dir::Caches=%s" % CACHE_APT_DIR, \
               "-o", "Debug::NoLocking=true", "-q=2"
    l = list(s.split(" "))
    l.extend(apt_args)
    print "Exec: %s" % " ".join(l)
    retcode = subprocess.call(l)
    return retcode

def replace_C_locale(l):
    return map(lambda a: a.replace("-C", ""), l)

def download_packages():
    safe_mkdirs(PARTIAL_DIR)
    safe_mkdirs(ETC_APT_DIR)
    safe_mkdirs(CACHE_APT_DIR)
    safe_mkdirs(VAR_DPKG_DIR)
    safe_mkdirs(PREFERENCES_DIR)
    safe_mkdirs(TRUSTED_DIR)
    safe_mkdirs(OUTPUT_DIR)
    os.system("touch %s" % DPKG_STATUS)
    
    os.chdir(TMP_DIR)
    subprocess.call(["cp", LOCAL_KEYRING, TRUSTED_DIR])
    write_sources_list()

    call_with_apt_args("apt-get update")
    
    for pkg in PACKAGES:
        call_with_apt_args("apt-cache policy %s" % pkg)
        if call_with_apt_args("apt-get download --allow-unauthenticated %s" % pkg) == 0:
            deb_files = glob.glob("%s_*.deb" % pkg)
            if not deb_files:
                print("No .deb files. apt error?")
                sys.exit(1)
            deb_file = deb_files[0]
            print "Exec: %s" % " ".join(["dpkg-deb", "--extract", deb_file, OUTPUT_DIR])
            if subprocess.call(["dpkg-deb", "--extract", deb_file, OUTPUT_DIR]) != 0:
                return False
            safe_remove(deb_file)
        else:
            return False
    return True

if __name__ == "__main__":
    pwd = os.getcwd()
    if not download_packages():
        sys.exit(1)
    os.chdir(pwd)
