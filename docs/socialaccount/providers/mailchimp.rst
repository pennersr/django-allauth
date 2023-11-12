MailChimp (OAuth2)
------------------

MailChimp has a simple API for working with your own data and a `good library`_
already exists for this use. However, to allow other MailChimp users to use an
app you develop, the OAuth2 API allows those users to give or revoke access
without creating a key themselves.

.. _good library: https://pypi.python.org/pypi/mailchimp3

Registering a new app
*********************

Instructions for generating your own OAuth2 app can be found at
https://developer.mailchimp.com/documentation/mailchimp/guides/how-to-use-oauth2/.
It is worth reading that carefully before following the instructions below.

Login via https://login.mailchimp.com/, which will redirect you to
``https://usX.admin.mailchimp.com/`` where the prefix ``usX`` (``X`` is an
integer) is the subdomain you need to connect to. Click on your username in the
top right corner and select *Profile*. On the next page select *Extras* then
click API keys, which should lead you to:

App registration (where ``X`` is dependent on your account)
    https://usX.admin.mailchimp.com/account/oauth2/

Fill in the form with the following URL for local development:

Development callback URL
    https://127.0.0.1:8000/accounts/mailchimp/login/callback/

Testing Locally
***************

Note the requirement of **https**. If you would like to test OAuth2
authentication locally before deploying a default django project will raise
errors because development mode does not support ``https``. One means of
circumventing this is to install ``django-extensions``::

    pip install django-extensions

add it to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_extensions',
        ...
    )

and then run::

    ./manage.py runserver_plus --cert cert

which should allow you to test locally via https://127.0.0.1:8000. Some
browsers may require enabling this on localhost and not support by default and
ask for permission.
