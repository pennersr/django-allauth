Line
----

scope options
  https://developers.line.biz/en/docs/line-login/integrate-line-login/#scopes

App registration, create a Line login channel (get your channel_id and channel_secret here)
    https://developers.line.biz/console/

Development callback URL
    http://127.0.0.1:8000/accounts/line/login/callback/

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
              'line': {
                  'APP': {
                      'client_id': 'LINE_LOGIN_CHANNEL_ID',
                      'secret': 'LINE_LOGIN_CHANNEL_SECRET'
                  },
                  "SCOPE": ['profile', 'openid', 'email']
              }
          }
