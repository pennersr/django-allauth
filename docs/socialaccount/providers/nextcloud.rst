NextCloud
---------

The following NextCloud settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        "nextcloud": {
            "APPS": [
                {
                    "client_id": "<insert-id>",
                    "secret": "<insert-secret>",
                    "settings": {
                        "server": "https://nextcloud.example.org",
                    }
                }
            ]
          }
    }


App registration (get your key and secret here)

    https://nextcloud.example.org/settings/admin/security
