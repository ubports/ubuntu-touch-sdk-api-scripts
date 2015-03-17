import json
import tempfile
import shutil
import re
import subprocess
import random
import string

from urlparse import urlsplit


def random_str(length):
    """Generates a random str to differentiate apps using the same domain."""
    return ''.join(random.choice(string.lowercase) for i in range(length))


def create_appname(domain):
    domain_nowww = re.sub('www\.', '', domain)
    appname = re.sub('\.', '', domain_nowww)
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
    displayname = data['displayname'].encode('UTF-8')
    domain = urlsplit(url)[1].encode('UTF-8')
    options = ' '.join(data['options'])
    appname = '%s-%s' % (create_appname(domain), random_str(3))
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

    # Build click package in tmp dir
    subprocess.call(['click', 'build', '--no-validate', tmp+'/resources'],
                    cwd=tmp)
    click_path = '%s/%s.%s_0.1_all.click' % (tmp, appname, nickname,)
    click_name = '%s.%s_0.1_all.click' % (appname, nickname,)
    return tmp, click_name, click_path