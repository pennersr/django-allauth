Lichess
-------

You do not need to create a new application on Lichess to use this provider.
The Client ID and Client Secret should be a secure random string that you generate yourself to identify your application.

Development callback URL
    http://127.0.0.1:8000/accounts/lichess/login/callback/

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
              'lichess': {
                  'APP': {
                      'client_id': 'LICHESS_CLIENT_ID',
                      'secret': 'LICHESS_CLIENT_SECRET'
                  },
              }
          }
