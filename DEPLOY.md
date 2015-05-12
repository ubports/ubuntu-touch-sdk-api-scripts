# Preparing a release

1. Follow the instructions in README.md to create a working environment
2. Merge and commit any approved code branches
3. Enter your virtualenv 

    source ./env/bin/activate
    
4. Create the tarball

    make tarball

4. Create a new release in Launchpad, use the bzr revno for the milestone

    https://launchpad.net/developer-ubuntu-com/trunk/+addrelease

5. Create a new download in Launchpad, uploaded the built tarball
   Use "website source" as the file description


# Requesting a deployment

We do not deploy this directly, instead we provide Canonical Sysadmins
with a tarball of the code which is deployed with a juju charm

1. Email ubuntu-platform@rt.canonical.com requesting a deployment
2. Inform them of the location of the new tarball (on Launchpad)
3. Instruct them to set build_label="${releasename}" using the release name from step 4 above

They will first deploy to the staging environment, where you will need
to verify the changes. If everything looks good, reply to the RT email
letting them know that it's ready to go to production. Repeat the checks
in production.
