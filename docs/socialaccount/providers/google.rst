Google
------

The Google provider is OAuth2 based.

More info:
    https://developers.google.com/identity/protocols/OAuth2


App registration
****************
Create a google app to obtain a key and secret through the developer console.

Google Developer Console
    https://console.developers.google.com/

After you create a project you will have to create a "Client ID" and fill in
some project details for the consent form that will be presented to the client.

Under "APIs & auth" go to "Credentials" and create a new Client ID. Probably
you will want a "Web application" Client ID. Provide your domain name or test
domain name in "Authorized JavaScript origins". Finally fill in
``http://127.0.0.1:8000/accounts/google/login/callback/`` in the
"Authorized redirect URI" field. You can fill multiple URLs, one for each test
domain. After creating the Client ID you will find all details for the Django
configuration on this page.

Users that login using the app will be presented a consent form. For this to
work additional information is required. Under "APIs & auth" go to
"Consent screen" and at least provide an email and product name.


Django configuration
********************
The app credentials are configured for your Django installation via the admin
interface. Create a new socialapp through ``/admin/socialaccount/socialapp/``.

Fill in the form as follows:

* Provider, "Google"
* Name, your pick, suggest "Google"
* Client id, is called "Client ID" by Google
* Secret key, is called "Client secret" by Google
* Key, is not needed, leave blank.

Optionally, you can specify the scope to use as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': [
                'profile',
                'email',
            ],
            'AUTH_PARAMS': {
                'access_type': 'online',
            },
            'OAUTH_PKCE_ENABLED': True,
        }
    }

By default (if you do not specify ``SCOPE``), ``profile`` scope is
requested, and optionally ``email`` scope depending on whether or not
``SOCIALACCOUNT_QUERY_EMAIL`` is enabled.

You must set ``AUTH_PARAMS['access_type']`` to ``offline`` in order to
receive a refresh token on first login and on reauthentication requests
(which is needed to refresh authentication tokens in the background,
without involving the user's browser). When unspecified, Google defaults
to ``online``.
