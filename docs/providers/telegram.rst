Telegram
--------

If the time of the telegram server differs from the time of your
server, then you may need to increase the authorization period using
the ``auth_date_validity`` parameter.
You can also set this parameter in Social applications settings as
json ``{"auth_date_validity": 100}``.
The default value of the ``auth_date_validity`` is 30 seconds.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'telegram': {
            'APP': {
                'client_id': '<bot_id>',
                'secret': '<bot token>',
            },
            'AUTH_PARAMS': {'auth_date_validity': 30},
        }
    }
