Globus
------

Registering an application:
    https://developers.globus.org/

By default, you will have access to the openid, profile, and offline_access
scopes.  With the offline_access scope, the API will provide you with a
refresh token.  For additional scopes, see the Globus API docs:

 https://docs.globus.org/api/auth/reference/

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'globus': {
            'SCOPE': [
                'openid',
                'profile',
                'email',
                'urn:globus:auth:scope:transfer.api.globus.org:all'
            ]
        }
    }
