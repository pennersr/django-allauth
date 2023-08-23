Authentiq
---------

Browse to https://www.authentiq.com/developers to get started.

App registration
    https://dashboard.authentiq.com/

Sign in or register with your Authentiq ID (select ``Download the app`` while signing in if you don't have Authentiq ID yet).

Development redirect URL
    http://localhost:8000/accounts/authentiq/login/callback/

While testing you can leave the ``Redirect URIs`` field empty in the dashboard. You can specify what identity details to request via the ``SCOPE`` parameter.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'authentiq': {
          'SCOPE': ['email', 'aq:name']
        }
    }

Valid scopes include: ``email``, ``phone``, ``address``, ``aq:name``, ``aq:location``. The default is to request a user's name, and email address if ``SOCIALACCOUNT_QUERY_EMAIL=True``. You can request and require a verified email address by setting ``SOCIALACCOUNT_EMAIL_VERIFICATION=True`` and ``SOCIALACCOUNT_EMAIL_REQUIRED=True``.
