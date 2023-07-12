Firefox Accounts
----------------

The Firefox Accounts provider is currently limited to Mozilla relying services
but there is the intention, in the future, to allow third-party services to
delegate authentication. There is no committed timeline for this.

The provider is OAuth2 based. More info:
    https://developer.mozilla.org/en-US/Firefox_Accounts

The following Firefox Accounts settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'fxa': {
            'SCOPE': ['profile'],
            'OAUTH_ENDPOINT': 'https://oauth.accounts.firefox.com/v1',
            'PROFILE_ENDPOINT': 'https://profile.accounts.firefox.com/v1',
        }
    }

SCOPE:
    Requested OAuth2 scope. Default is ['profile'], which will work for
    applications on the Mozilla trusted whitelist. If your application is not
    on the whitelist, then define SCOPE to be ['profile:email', 'profile:uid'].

OAUTH_ENDPOINT:
    Explicitly set the OAuth2 endpoint. Default is the production endpoint
    "https://oauth.accounts.firefox.com/v1".

PROFILE_ENDPOINT:
    Explicitly set the profile endpoint. Default is the production endpoint
    and is "https://profile.accounts.firefox.com/v1".
