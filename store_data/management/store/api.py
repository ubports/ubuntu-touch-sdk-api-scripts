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


class GadgetSnapData(object):
    data = {}

    def get_data(self):
        params = urlencode({'q': 'content:oem'})
        url = PACKAGE_API + "?%s" % params
        req = Request(url)
        req.add_header('X-Ubuntu-Frameworks', 'ubuntu-core-15.04-dev1')
        # XXX: This is supposed to work, but doesn't.
        # req.add_header('X-Ubuntu-Release',
        #                '[15.04-core|rolling-core|rolling-personal]')
        req.add_header('Accept', 'application/hal+json')
        f = urlopen(req)
        s = f.read().decode('utf-8')
        f.close()
        packages = json.loads(s)
        self.data = packages['_embedded']['clickindex:package']

    def get_additional_snap_data(self):
        for entry in self.data:
            snap_api_url = entry['_links']['self']['href']
            req = Request(snap_api_url)
            req.add_header('Accept', 'application/hal+json')
            f = urlopen(req)
            s = f.read().decode('utf-8')
            f.close()
            data = json.loads(s)
            entry['screenshot_urls'] = []
            if data['screenshot_url']:
                entry['screenshot_urls'] += [data['screenshot_url']]
            if data['screenshot_urls']:
                entry['screenshot_urls'].extend(data['screenshot_urls'])
            entry['description'] = data['description']

    def __init__(self):
        self.get_data()
        self.get_additional_snap_data()
