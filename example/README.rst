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

Now we need to create the database tables and an admin user.
On Django 1.6 and below, run the following and when prompted to create a
superuser choose yes and follow the instructions:

::

    $ python manage.py syncdb --migrate

On Django 1.7 and above:

::

    $ python manage.py migrate
    $ python manage.py createsuperuser


Now you need to run the Django development server:

::

    $ python manage.py runserver

You should then be able to open your browser on http://127.0.0.1:8000 and
see a page with links to sign in or sign up.

Example Bootstrap templates
---------------------------

There are templates in the ``templates/bootstrap/allauth/account/`` that can
be used with Twitter's `Bootstrap <http://twitter.github.com/bootstrap/>`_
library. To use these templates, in addition to the above commands, you
will need to

::

    $ pip install django-bootstrap-form

and put ``bootstrapform`` into ``INSTALLED_APPS`` in your ``settings.py`` file.
