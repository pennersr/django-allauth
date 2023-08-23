GitHub
------

App registration (get your key and secret here)
    https://github.com/settings/applications/new

Development callback URL
    http://127.0.0.1:8000/accounts/github/login/callback/

If you want more than just read-only access to public data, specify the scope
as follows. See https://developer.github.com/v3/oauth/#scopes for details.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'github': {
            'SCOPE': [
                'user',
                'repo',
                'read:org',
            ],
        }
    }

Enterprise Support
******************

If you use GitHub Enterprise add your server URL to your Django settings as
follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'github': {
            'GITHUB_URL': 'https://your.github-server.domain',
        }
    }
