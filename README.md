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
