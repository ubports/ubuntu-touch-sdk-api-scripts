import logging
import os
import subprocess


class SourceCode():
    def __init__(self, branch_origin, checkout_location):
        self.branch_origin = branch_origin
        self.checkout_location = checkout_location

    def get(self):
        if self.branch_origin.startswith('lp:') and \
           os.path.exists('/usr/bin/bzr'):
            return subprocess.call([
                'bzr', 'checkout', '--lightweight', self.branch_origin,
                self.checkout_location])
        if self.branch_origin.startswith('https://github.com') and \
           self.branch_origin.endswith('.git') and \
           os.path.exists('/usr/bin/git'):
            return subprocess.call([
                'git', 'clone', '-q', self.branch_origin,
                self.checkout_location])
        logging.error(
            'Branch format "{}" not understood.'.format(self.branch_origin))
        return 1
