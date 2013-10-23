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
    $ python manage.py syncdb
    $ python manage.py runserver

You should then be able to open your browser on http://127.0.0.1:8000 and
see a page with links to sign in or sign up.

Sending emails on the dev environment
-------------------------------------

When you try to "sign up" a user, you will notice that the confirmation email is
not really sent, but instead it is printed on the stdout.  This is because we
use Django's console email backend ::

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

In production you must of course remove this line from ``settings.py`` and
set up an email server properly.

Another option you can follow in you DEV environment is to start Python's StdLib
SMTP server on a different console::

    python -m smtpd -n -c DebuggingServer localhost:1025

and let Django use it by putting in your ``settings.py``::

    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

For more info, you may look here:
http://stackoverflow.com/questions/4642011/test-sending-email-without-email-server

Example Bootstrap templates
---------------------------

There are templates in the ``templates/bootstrap/allauth/account/`` that can
be used with Twitter's `Bootstrap <http://twitter.github.com/bootstrap/>`_
library. To use these templates, in addition to the above commands, you
will need to

::

    $ pip install django-bootstrap-form

and put ``bootstrapform`` into ``INSTALLED_APPS`` in your ``settings.py`` file.


