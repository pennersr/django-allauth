Patreon
-------

The following Patreon settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'patreon': {
            'VERSION': 'v1',
            'SCOPE': ['pledges-to-me', 'users', 'my-campaign'],
        }
    }

VERSION:
    API version. Either ``v1`` or ``v2``. Defaults to ``v1``.

SCOPE:
    Defaults to the scope above if using API v1. If using v2, the scope defaults to ``['identity', 'identity[email]', 'campaigns', 'campaigns.members']``.

API documentation:
    https://www.patreon.com/platform/documentation/clients

App registration (get your key and secret for the API here):
    https://www.patreon.com/portal/registration/register-clients

Development callback URL
    http://127.0.0.1:8000/accounts/patreon/login/callback/
