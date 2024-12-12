Telegram
--------

Telegram does not strictly regulate the authorization expiration
time, so you may need to set your own expiration time, which can be
less than the default value.
You can also set this parameter in Social applications settings as
json ``{"auth_date_validity": 100}``.
The default value of the ``auth_date_validity`` is 30 seconds.


.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'telegram': {
            'APP': {
                'client_id': '<bot_id>',

                # NOTE: For the secret, be sure to provide the complete bot token,
                # which typically includes the bot ID as a prefix.
                'secret': '<bot token>',
            },
            'AUTH_PARAMS': {'auth_date_validity': 30},
        }
    }

.. code-block:: python


Attention! If your server time is different from the telegram
server time, you need NTP.
