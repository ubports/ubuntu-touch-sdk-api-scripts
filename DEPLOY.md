# Preparing a release

1. Follow the instructions in README.md to create a working environment
2. Merge and commit any approved code branches
3. Run `make update-pip-cache` if there have been pip packages changes.
   Don't forget to commit the new dependencies branch revno to trunk.
4. Merge lp:developer-ubuntu-com on lp:developer-ubuntu-com/production
5. Note the revno of lp:developer-ubuntu-com/production commit you want
   to deploy


# Doing a staging deployment

1. Connect to the staging server and switch to the correct user.
2. run `juju set devportal-app build_label="<production revno>"`.


# Requesting a production deployment

1. Email ubuntu-platform@rt.canonical.com requesting a deployment
2. Instruct them to run 
   `juju set devportal-app build_label="<production revno>"`
