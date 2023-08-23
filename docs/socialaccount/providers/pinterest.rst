Pinterest
---------

The Pinterest OAuth2 documentation:

    # v1  # has been deprecated
    https://developers.pinterest.com/docs/api/overview/#authentication

    # v3  # plan to enforce an end of life on June 30, 2023.
    https://developers.pinterest.com/docs/redoc/#section/User-Authorization

    # v5
    https://developers.pinterest.com/docs/getting-started/authentication/

You can optionally specify additional permissions to use. If no ``SCOPE``
value is set, the Pinterest provider will use reading scope by default.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'pinterest': {
            'SCOPE': ['user_accounts:read'],
            "API_VERSION": "v5",
        }
    }

SCOPE:
    For a full list of scope options, see

    # v1
    https://developers.pinterest.com/docs/api/overview/#scopes

    # v3
    https://developers.pinterest.com/docs/redoc/#section/User-Authorization/OAuth-scopes

    # v5
    https://developers.pinterest.com/docs/getting-started/scopes/
