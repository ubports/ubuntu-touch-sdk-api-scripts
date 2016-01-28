# Setting up the development environment

1. Check out the branch
2. Change directory to the branch location
3. Install the apt requirements:

    sudo apt install python-dev python-django python-django-south python-psycopg2 pwgen virtualenv

4. Setup your local dev environment:

    make dev

5. To run the site:

    make run

At the time of writing, we don't have a button to log in. To be able to do so, go to this URL
in development mode:

    http://localhost:8000/openid/login

# Using sample data

If you want to populate the database with sample content, you can follow these instructions:

    bzr branch lp:~mhall119/+junk/devportal_backup ../dbbackup
    ./env/bin/python manage.py flush --noinput
    echo "delete from auth_permission;" | ./env/bin/python manage.py dbshell
    ./env/bin/python manage.py loaddata ../dbbackup/dbdump.json
    ./env/bin/python manage.py migrate --noinput
    ./env/bin/python manage.py initdb

# Managing translations

To manage translations, run
    make translations

To simply update the .pot file (included in the command above), run:
    ./env/bin/python manage.py update-template
