DigitalOcean
------------

App registration (get your key and secret here)
    https://cloud.digitalocean.com/settings/applications

Development callback URL
    http://127.0.0.1:8000/accounts/digitalocean/login/callback/

With the acquired access token you will have read permissions on the API by
default.  If you also need write access specify the scope as follows.  See
https://developers.digitalocean.com/documentation/oauth/#scopes for details.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'digitalocean': {
            'SCOPE': [
                'read write',
            ],
        }
    }
