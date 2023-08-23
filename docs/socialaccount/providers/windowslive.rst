Windows Live
------------

The Windows Live provider currently does not use any settings in
``SOCIALACCOUNT_PROVIDERS``.

App registration (get your key and secret here)
    https://apps.dev.microsoft.com/#/appList

Development callback URL
    http://localhost:8000/accounts/windowslive/login/callback/

Microsoft calls the "client_id" an "Application Id" and it is a UUID. Also,
the "client_secret" is not created by default, you must edit the application
after it is created, then click "Generate New Password" to create it.
