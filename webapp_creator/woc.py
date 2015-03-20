import json
import tempfile
import shutil
import re
import subprocess
from urlparse import urlsplit


def create_appname(name):
    name = re.sub('[^0-9a-zA-Z]+', '', name)
    appname = name[:20].lower()
    return appname


def create_tmp(appname, domain):
    tmp = tempfile.mkdtemp()
    shutil.copytree('webapp_creator/resources', tmp+"/resources")
    shutil.move(tmp+'/resources/appname.apparmor',
                tmp+"/resources/%s.apparmor" % (appname,))
    shutil.move(tmp+'/resources/appname.desktop',
                tmp+"/resources/%s.desktop" % (appname,))
    return tmp


def create(data):
    nickname = data['nickname'].encode('UTF-8')
    url = data['url'].encode('UTF-8')
    version = data['version'].encode('UTF-8')
    displayname = data['displayname'].encode('UTF-8')
    domain = urlsplit(url)[1].encode('UTF-8')
    options = ' '.join(data['options'])
    appname = create_appname(displayname)
    tmp = create_tmp(appname, domain)

    # Create icon
    if 'icon' in data:
        appicon = data['icon'].name.encode('UTF-8')
        with open(tmp+"/resources/%s" % (appicon,), 'wb+') as f:
            for chunk in data['icon'].chunks():
                f.write(chunk)

    # Create desktop file
    file_desktop = open("webapp_creator/resources/appname.desktop").read()
    desktop_new = file_desktop.format(appname=appname,
                                      displayname=displayname,
                                      container_options=options,
                                      domain=domain,
                                      url=url,
                                      appicon=appicon)
    with open(tmp+"/resources/%s.desktop" % (appname,), "w") as f:
        f.write(desktop_new)
        f.close()

    # Create manifest
    manifest_new = json.loads(
        open("webapp_creator/resources/manifest.json").read())
    manifest_new['name'] = '%s.%s' % (appname, nickname,)
    manifest_new['title'] = displayname
    manifest_new['version'] = version
    manifest_new['description'] = 'Webapp for %s' % (domain,)
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

    # Build click package in tmp dir
    subprocess.call(['click', 'build', tmp+'/resources'],
                    cwd=tmp)
    click_path = '%s/%s.%s_%s_all.click' % (tmp, appname, nickname, version)
    click_name = '%s.%s_%s_all.click' % (appname, nickname, version)
    return tmp, click_name, click_path
