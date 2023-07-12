Gitea
-----

App registration (get your key and secret here)
    https://gitea.com/user/settings/applications

Development callback URL
    http://127.0.0.1:8000/accounts/gitea/login/callback/


Self-hosted Support
*******************

If you use a self-hosted Gitea instance add your server URL to your Django settings as
follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'gitea': {
            'GITEA_URL': 'https://your.gitea-server.domain',
        }
    }
