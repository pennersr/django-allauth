Xero
-----

App registration (create an App here)
    https://developer.xero.com/app/manage/

Development callback URL
    http://domain.com/accounts/xero/login/callback/

Add the following configuration to your settings:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        "xero": {
            "APP": {
                # Your Client ID (managed in the "Configuration" page).
                "client_id": "your_client_id",
                # The Client Secret (managed in the "Configuration" page).
                "secret": "secret",
                }
            }
        }
    }

