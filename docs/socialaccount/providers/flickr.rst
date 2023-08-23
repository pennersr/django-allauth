Flickr
------

App registration (get your key and secret here)
    https://www.flickr.com/services/apps/create/

You can optionally specify the application permissions to use. If no ``perms``
value is set, the Flickr provider will use ``read`` by default.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'flickr': {
            'AUTH_PARAMS': {
                'perms': 'write',
            }
        }
    }

More info:
    https://www.flickr.com/services/api/auth.oauth.html#authorization
