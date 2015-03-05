import json
import tempfile
import shutil
import re
import subprocess

from urlparse import urlsplit
from urllib import urlretrieve


def create_appname(domain):
    domain_nowww = re.sub('www\.', '', domain)
    appname = re.sub('\.', '', domain_nowww)
    return appname


def create_tmp(appname, domain):
    tmp = tempfile.mkdtemp()
    shutil.copytree('webapp_creator/resources', tmp+"/resources")
    shutil.move(tmp+'/resources/appname.png',
                tmp+"/resources/%s.png" % (appname,))
    shutil.move(tmp+'/resources/appname.apparmor',
                tmp+"/resources/%s.apparmor" % (appname,))
    shutil.move(tmp+'/resources/appname.desktop',
                tmp+"/resources/%s.desktop" % (appname,))
    # FIXME BYOI
    urlretrieve('http://grabicon.com/icon?domain=%s&size=32&origin=example.com' % (domain,), tmp + "/resources/%s.png" % (appname,))
    return tmp


def create(data):
    nickname = data['nickname']
    url = data['url']
    displayname = data['displayname']
    domain = urlsplit(url)[1]
    appname = create_appname(domain)
    tmp = create_tmp(appname, domain)

    # Create desktop file
    file_desktop = open("webapp_creator/resources/appname.desktop").read()
    desktop_new = file_desktop.format(appname=appname,
                                      displayname=displayname,
                                      container_options='',
                                      domain=domain,
                                      url=url,)
    with open(tmp+"/resources/%s.desktop" % (appname,), "w") as f:
        f.write(desktop_new)
        f.close()

    # Create manifest
    manifest_new = json.loads(
        open("webapp_creator/resources/manifest.json").read())
    manifest_new['name'] = '%s.%s' % (appname, nickname,)
    manifest_new['title'] = displayname
    manifest_new['description'] = 'Web app for %s' % (domain,)
    manifest_new['hooks'] = {appname:
                             {'apparmor': '%s.apparmor' % (appname,),
                              'desktop': '%s.desktop' % (appname,)
                              }
                             }
    manifest_new['maintainer'] = '%s <%s>' % (data['fullname'],
                                              data['email'],)
    with open(tmp+"/resources/manifest.json", "w") as f:
        f.write(json.dumps(manifest_new))
        f.close()

    # Build click package
    subprocess.call(['click', 'build', tmp+'/resources'])
    # FIXME support click staying in /tmp
    click_path = '%s.%s_0.1_all.click' % (appname, nickname,)
    click_name = '%s.%s_0.1_all.click' % (appname, nickname,)
    return tmp, click_name, click_path
