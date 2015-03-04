#! /usr/bin/python3
import json
import tempfile
import shutil
import sys
import re

from urlparse import urlsplit
from urllib import urlretrieve


def create(url):
    nickname = "ubuntudev"
    domain = urlsplit(url)[1]
    domain_nowww = re.sub('www\.', '', domain)
    appname = re.sub('\.', '', domain_nowww)
    displayname = ' '.join(re.sub('.*//', '', domain_nowww).split('.')[:-1][::-1]).title()
    file_desktop = open("webapp_creator/resources/appname.desktop").read()
    manifest_new = json.loads(open("webapp_creator/resources/manifest.json").read())

    desktop_new = file_desktop.format(appname=appname,
                                      displayname=displayname,
                                      container_options='',
                                      domain=domain,
                                      url=url,)

    manifest_new['name'] = '%s.%s' % (appname, nickname,)
    manifest_new['title'] = displayname
    manifest_new['description'] = 'Web app for %s' % (domain,)
    manifest_new['hooks'] = {appname:
                                {'apparmor': '%s.apparmor' % (appname,),
                                 'desktop': '%s.desktop' % (appname,)
                                 }
                             }
    manifest_new['maintainer'] = '%s <%s@ubuntu.com>' % (nickname, nickname,)

    tmp = tempfile.mkdtemp()
    shutil.copytree('webapp_creator/resources', tmp+"/resources")
    shutil.move(tmp+'/resources/appname.png',
                tmp+"/resources/%s.png" % (appname,))
    shutil.move(tmp+'/resources/appname.apparmor',
                tmp+"/resources/%s.apparmor" % (appname,))
    shutil.move(tmp+'/resources/appname.desktop',
                tmp+"/resources/%s.desktop" % (appname,))
    urlretrieve('http://grabicon.com/icon?domain=%s&size=32&origin=example.com' %(domain,) ,tmp+"/resources/%s.png" % (appname,))

    with open(tmp+"/resources/%s.desktop" % (appname,), "w") as f:
        f.write(desktop_new)
        f.close()

    with open(tmp+"/resources/manifest.json", "w") as f:
        f.write(json.dumps(manifest_new))
        f.close()

# Disabled click stuff
#
#    from click.build import ClickBuilder
#    builder = ClickBuilder()
#    builder.add_file(tmp+"/resources/", "./")
#    path = builder.build(tmp, manifest_path=tmp+"/resources/manifest.json")
#    shutil.copy(path, '.')

# Delete working dirs
#    shutil.rmtree(tmp)
    return tmp
#    return path
