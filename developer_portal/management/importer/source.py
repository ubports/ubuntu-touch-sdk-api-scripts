import logging
import os
import subprocess


class SourceCode():
    def __init__(self, origin, checkout_location, branch_name,
                 post_checkout_command):
        self.origin = origin
        self.checkout_location = checkout_location
        self.branch_name = branch_name
        self.post_checkout_command = post_checkout_command

    def get(self):
        res = self._get_branch()
        if res == 0 and self.post_checkout_command:
            res = self._post_checkout()
            return res
        return res

    def _get_branch(self):
        if self.origin.startswith('lp:') and \
           os.path.exists('/usr/bin/bzr'):
            return subprocess.call([
                'bzr', 'checkout', '--lightweight', self.origin,
                self.checkout_location])
        if self.origin.startswith('https://github.com') and \
           self.origin.endswith('.git') and \
           os.path.exists('/usr/bin/git'):
            retcode = subprocess.call([
                'git', 'clone', '-q', self.origin,
                self.checkout_location])
            if retcode == 0 and self.branch_name:
                retcode = subprocess.call(['git', 'checkout',
                    self.branch_name])
            return retcode
        logging.error(
            'Branch format "{}" not understood.'.format(self.origin))
        return 1

    def _post_checkout(self):
        process = subprocess.Popen(self.post_checkout_command.split(),
                                   stdout=subprocess.PIPE)
        (out, err) = process.communicate()
        retcode = process.wait()
        if retcode != 0:
            logging.error(out)
        return retcode
