Reddit
------

App registration (get your key and secret here)
    https://www.reddit.com/prefs/apps/

Development callback URL
    http://localhost:8000/accounts/reddit/login/callback/

By default, access to Reddit is temporary. You can specify the ``duration``
auth parameter to make it ``permanent``.

You can optionally specify additional permissions to use. If no ``SCOPE``
value is set, the Reddit provider will use ``identity`` by default.

In addition, you should override your user agent to comply with Reddit's API
rules, and specify something in the format
``<platform>:<app ID>:<version string> (by /u/<reddit username>)``. Otherwise,
you will risk additional rate limiting in your application.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'reddit': {
            'AUTH_PARAMS': {'duration': 'permanent'},
            'SCOPE': ['identity', 'submit'],
            'USER_AGENT': 'django:myappid:1.0 (by /u/yourredditname)',
        }
    }
