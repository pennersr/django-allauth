Auth0
-----

App registration (get your key and secret here)
    https://manage.auth0.com/#/clients

Development callback URL
    http://localhost:8000/accounts/auth0/login/callback/


You'll need to specify the base URL for your Auth0 domain:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'auth0': {
            'AUTH0_URL': 'https://your.auth0domain.auth0.com',
            'OAUTH_PKCE_ENABLED': True,
        }
    }
