===============================
Running the example application
===============================

Assuming you use virtualenv, follow these steps to download and run the
django-allauth example application in this directory:

::

    $ git clone git@github.com:pennersr/django-allauth.git
    $ cd django-allauth/examples/regular-django
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install "../..[mfa,saml]"

Now we need to create the database tables and an admin user.
Run the following and when prompted to create a superuser choose yes and
follow the instructions:

::

    $ python manage.py migrate
    $ python manage.py createsuperuser


Now you need to run the Django development server:

::

    $ python manage.py runserver

You should then be able to open your browser on http://127.0.0.1:8000 and
see a page with links to sign in or sign up.
