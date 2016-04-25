from md_importer.importer import logger

import os
import shutil
import subprocess


class SourceCode():
    def __init__(self, origin, checkout_location, branch_name,
                 post_checkout_command):
        self.origin = origin
        self.checkout_location = checkout_location
        self.branch_name = branch_name
        self.post_checkout_command = post_checkout_command

    def get(self):
        res = self._get_repo()
        if res == 0 and self.post_checkout_command:
            res = self._post_checkout()
            return res
        return res

    def _get_repo(self):
        if os.path.exists(self.origin):
            shutil.copytree(
                self.origin,
                self.checkout_location)
            return 0
        if self.origin.startswith('lp:') and \
           os.path.exists('/usr/bin/bzr'):
            return subprocess.call([
                'bzr', 'checkout', '--lightweight', self.origin,
                self.checkout_location])
        if self.origin.startswith('https://github.com') and \
           self.origin.endswith('.git') and \
           os.path.exists('/usr/bin/git'):
            retcode = subprocess.call([
                'git', 'clone', '--quiet', self.origin,
                self.checkout_location])
            if retcode == 0 and self.branch_name:
                pwd = os.getcwd()
                os.chdir(self.checkout_location)
                retcode = subprocess.call(['git', 'checkout', '--quiet',
                                           self.branch_name])
                os.chdir(pwd)
            return retcode
        logger.error(
            'Repo format "{}" not understood.'.format(self.origin))
        return 1

    def _post_checkout(self):
        pwd = os.getcwd()
        os.chdir(self.checkout_location)
        process = subprocess.Popen(self.post_checkout_command.split(),
                                   stdout=subprocess.PIPE)
        (out, err) = process.communicate()
        retcode = process.wait()
        os.chdir(pwd)
        if retcode != 0:
            logger.error(out)
        return retcode
