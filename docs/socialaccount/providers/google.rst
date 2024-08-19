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

After you create a project, you will have to create an OAuth client ID and fill
in some project details for the consent form that will be presented to the
client:

#. Under "APIs & Services", go to "Credentials", click "Create credentials" and
   create a new "OAuth client ID". Probably you will want to choose "Web
   application" as the application type. Provide your domain name or test
   domain name in "Authorized JavaScript origins". Finally, fill in the
   "Authorized redirect URIs" field with URLs like
   ``http://example.com/accounts/google/login/callback/`` , replacing the
   domain name with your domain name, or with ``127.0.0.1:8000`` for testing.
   After creating the OAuth client ID, make a note of the client ID and the
   client secret, as you will need it later.

#. Users that log in using the app will be presented a consent form. For this
   to work, additional information is required. Under "APIs & Services", go to
   "OAuth consent screen" and at least provide an email address and a product
   name.


Django configuration
********************

Don't forget to add the Google provider to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'allauth.socialaccount.providers.google',
    ]

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

By default, the userinfo endpoint will not be fetched. In most cases,
this will be fine, as most in scope user data is gained via decoding
the JWT. However if users have a private style of avatar_url
then this will not ordinarily be returned in the JWT and
as such, subsequent calls to get_avatar_url will return None.

You can optionally specify the following setting so that the userinfo
endpoint will be used to populate the avatar_url for those users
who have a private style of avatar_url.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'FETCH_USERINFO' : True
        }
    }

One Tap Sign-In
***************

One Tap Sign-In can be enabled by adding a snippet like this snippet to your
template::

    <script src="//accounts.google.com/gsi/client" async></script>
    <div id="g_id_onload"
         data-client_id="123-secret.apps.googleusercontent.com"
         data-login_uri="{% url 'google_login_by_token' %}">
    </div>

Follow the `Sign In with Google for Web`_ guide for more information.

.. _Sign In with Google for Web: https://developers.google.com/identity/gsi/web/guides/overview
