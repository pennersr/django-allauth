Battle.net
----------

The Battle.net OAuth2 authentication documentation
    https://develop.battle.net/documentation/guides/using-oauth

Register your app here (Blizzard account required)
    https://develop.battle.net/access/clients/create

Development callback URL
    https://localhost:8000/accounts/battlenet/login/callback/

Note that in order to use battletags as usernames, you are expected to override
either the ``username`` field on your User model, or to pass a custom validator
which will accept the ``#`` character using the ``ACCOUNT_USERNAME_VALIDATORS``
setting. Such a validator is available in
``socialaccount.providers.battlenet.validators.BattletagUsernameValidator``.

The following Battle.net settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'battlenet': {
            'SCOPE': ['wow.profile', 'sc2.profile'],
            'REGION': 'us',
        }
    }

SCOPE:
    Scope can be an array of the following options: ``wow.profile`` allows
    access to the user's World of Warcraft characters. ``sc2.profile`` allows
    access to the user's StarCraft 2 profile. The default setting is ``[]``.

REGION:
    Either ``apac``, ``cn``, ``eu``, ``kr``, ``sea``, ``tw`` or ``us``

    Sets the default region to use, can be overridden using query parameters
    in the URL, for example: ``?region=eu``. Defaults to ``us``.
