# Setting up the development environment

1. Check out the branch
2. Change directory to the branch location
3. Install the apt requirements and set up a virtual env

    sudo apt-get install python-dev python-django python-django-south python-psycopg2 pwgen
    virtualenv ./env
    ./env/bin/pip install -r requirements.txt
    ./env/bin/python manage.py syncdb --noinput --migrate
    ./env/bin/python manage.py initdb
    ./env/bin/python manage.py collectstatic --noinput

To run the site:

    ./env/bin/python manage.py runserver

At the time of writing, we don't have a button to log in. To be able to do so, go to this URL
in development mode:

    http://localhost:8000/openid/login

# Using sample data

If you want to populate the database with sample content, you can follow these instructions:

    bzr branch lp:~mhall119/+junk/devportal_backup ../dbbackup
    ./env/bin/python manage.py flush --noinput
    echo "delete from auth_permission;" | ./env/bin/python manage.py dbshell
    ./env/bin/python manage.py loaddata ../dbbackup/dbdump.json
    ./env/bin/python manage.py syncdb --noinput --all
    ./env/bin/python manage.py initdb

# Managing translations

For updating the .pot file run

    ./env/bin/python manage.py makemessages --keep-pot -i "env/*" --all
    ./env/bin/python manage.py compilemessages
