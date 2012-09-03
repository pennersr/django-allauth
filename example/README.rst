===============================
Running the example application
===============================

Assuming you use virtualenv, follow these steps to download and run the
django-allauth example application in this directory:

::

    $ git clone git://github.com/pennersr/django-allauth.git
    $ cd django-allauth/example
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ python manage.py runserver

You should then be able to open your browser on http://127.0.0.1:8000 and
see a page with links to sign in or sign up.
