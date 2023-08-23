Bitbucket
---------

App registration (get your key and secret here)
    https://bitbucket.org/account/user/{{yourusername}}/oauth-consumers/new

Make sure you select the Account:Read permission.

Development callback URL
    http://127.0.0.1:8000/accounts/bitbucket_oauth2/login/callback/

Note that Bitbucket calls the ``client_id`` *Key* in their user interface.
Don't get confused by that; use the *Key* value for your ``client_id`` field.
