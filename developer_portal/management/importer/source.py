import logging
import os
import subprocess


class SourceCode():
    def __init__(self, branch_origin, checkout_location,
                 post_checkout_command):
        self.branch_origin = branch_origin
        self.checkout_location = checkout_location
        self.post_checkout_command = post_checkout_command

    def get(self):
        res = self._get_branch()
        if res == 0 and self.post_checkout_command:
            res = self._post_checkout()
            return res
        return res

    def _get_branch(self):
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

    def _post_checkout(self):
        process = subprocess.Popen(self.post_checkout_command.split(),
                                   stdout=subprocess.PIPE)
        (out, err) = process.communicate()
        retcode = process.wait()
        if retcode != 0:
            logging.error(out)
        return retcode
