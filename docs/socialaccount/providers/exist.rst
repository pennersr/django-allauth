Exist
-----

Register your OAuth2 app in apps page:

    https://exist.io/account/apps/

During development set the callback url to:

    http://localhost:8000/accounts/exist/login/callback/

In production replace localhost with whatever domain you're hosting your app on.

If your app is writing to certain attributes you need to specify this during the
creation of the app. For a full list of scopes see:

https://developer.exist.io/reference/authentication/oauth2/#scopes

The following Exist settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'exist': {
            'SCOPE': ['mood_read', 'health_read', 'productivity_read'],
        }
    }

SCOPE:
    The default scopes are listed above. For reading additional attributes or writing data see
    https://developer.exist.io/reference/authentication/oauth2/#scopes.

For more information:
OAuth documentation: https://developer.exist.io/reference/authentication/oauth2
API documentation: https://developer.exist.io/reference/important_values/
