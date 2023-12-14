LinkedIn
--------

You can specify the scope and fields to fetch as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'linkedin': {
            'SCOPE': [
                'r_basicprofile',
                'r_emailaddress'
            ],
            'PROFILE_FIELDS': [
                'id',
                'first-name',
                'last-name',
                'email-address',
                'picture-url',
                'public-profile-url',
            ]
        }
    }

By default, ``r_emailaddress`` scope is required depending on whether or
not ``SOCIALACCOUNT_QUERY_EMAIL`` is enabled.

Note: if you are experiencing issues where it seems as if the scope has no
effect you may be using an old LinkedIn app that is not scope enabled.
Please refer to
``https://developer.linkedin.com/forum/when-will-old-apps-have-scope-parameter-enabled``
for more background information.

Furthermore, we have experienced trouble upgrading from OAuth 1.0 to OAuth 2.0
using the same app. Attempting to do so resulted in a weird error message when
fetching the access token::

    missing required parameters, includes an invalid parameter value, parameter more then once. : Unable to retrieve access token : authorization code not found

If you are using tokens originating from the mobile SDK, you will need to specify
additional headers:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'linkedin': {
            'HEADERS': {
                'x-li-src': 'msdk'
            }
        }
    }

App registration (get your key and secret here)
    https://www.linkedin.com/secure/developer?newapp=

Authorized Redirect URLs (OAuth2)
*********************************
Add any you need (up to 200) consisting of:

    {``ACCOUNT_DEFAULT_HTTP_PROTOCOL``}://{hostname}{:optional_port}/{allauth_base_url}/linkedin_oauth2/login/callback/

For example when using the built-in django server and default settings:

    http://localhost:8000/accounts/linkedin_oauth2/login/callback/


Development "Accept" and "Cancel" redirect URL (OAuth 1.0a)
***********************************************************
    Leave the OAuth1 redirect URLs empty.
