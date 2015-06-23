import json
import sys

if sys.version_info.major == 2:
    from urllib import urlencode
    from urllib2 import Request, urlopen
else:
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen


STORE_URL = 'https://search.apps.ubuntu.com'
PACKAGE_API = STORE_URL + '/api/v1/search'


def get_oem_snap_entries():
    params = urlencode({'q': 'content:oem'})
    url = PACKAGE_API + "?%s" % params
    req = Request(url)
    req.add_header('X-Ubuntu-Frameworks', 'ubuntu-core-15.04-dev1')
    # req.add_header('X-Ubuntu-Release',
    #                '[15.04-core|rolling-core|rolling-personal]')
    req.add_header('Accept', 'application/hal+json')
    f = urlopen(req)
    s = f.read().decode('utf-8')
    f.close()
    packages = json.loads(s)
    return packages['_embedded']['clickindex:package']
