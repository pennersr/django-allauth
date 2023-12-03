GitLab
------

The GitLab provider works by default with https://gitlab.com. It allows you
to connect to your private GitLab server and use GitLab as an OAuth2
authentication provider as described in GitLab docs at
http://doc.gitlab.com/ce/integration/oauth_provider.html

The following GitLab settings are available, if unset https://gitlab.com will
be used, with a ``read_user`` scope.

GITLAB_URL:
    Override endpoint to request an authorization and access token. For your
    private GitLab server you use: ``https://your.gitlab.server.tld``

SCOPE:
    The ``read_user`` scope is required for the login procedure, and is the default.
    If more access is required, the scope should be set here.

Example:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        "gitlab": {
            "SCOPE": ["api"],
            "APPS": [
                {
                    "client_id": "<insert-id>",
                    "secret": "<insert-secret>",
                    "settings": {
                        "gitlab_url": "https://your.gitlab.server.tld",
                    }
                }
            ]
        },
    }
