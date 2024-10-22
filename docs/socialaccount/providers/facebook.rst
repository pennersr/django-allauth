Facebook
--------

For Facebook both OAuth2, Facebook Connect Javascript SDK and even
`Limited Login <https://developers.facebook.com/docs/facebook-login/limited-login>`_
are supported. You can even mix and match.

An advantage of the Javascript SDK may be a more streamlined user
experience as you do not leave your site. Furthermore, you do not need
to worry about tailoring the login dialog depending on whether or not
you are using a mobile device. Yet, relying on Javascript may not be
everybody's cup of tea.

To initiate a login use:

.. code-block:: python

    {% load socialaccount %}
    {% providers_media_js %}
    <a href="{% provider_login_url "facebook" %}">Facebook Connect</a>

The following Facebook settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'facebook': {
            'METHOD': 'oauth2',  # Set to 'js_sdk' to use the Facebook connect SDK
            'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
            'SCOPE': ['email', 'public_profile'],
            'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
            'INIT_PARAMS': {'cookie': True},
            'FIELDS': [
                'id',
                'first_name',
                'last_name',
                'middle_name',
                'name',
                'name_format',
                'picture',
                'short_name'
            ],
            'EXCHANGE_TOKEN': True,
            'LOCALE_FUNC': 'path.to.callable',
            'VERIFIED_EMAIL': False,
            'VERSION': 'v13.0',
            'GRAPH_API_URL': 'https://graph.facebook.com/v13.0',
        }
    }

METHOD:
    Either ``js_sdk`` or ``oauth2``. The default is ``oauth2``.

SDK_URL:
    If needed, use ``SDK_URL`` to override the default Facebook JavaScript SDK
    URL, ``//connect.facebook.net/{locale}/sdk.js``. This may be necessary, for
    example, when using the `Customer Chat Plugin <https://developers.facebook.com/docs/messenger-platform/discovery/customer-chat-plugin/sdk#install>`_.
    If the ``SDK_URL`` contains a ``{locale}`` format string named argument,
    the locale given by the ``LOCALE_FUNC`` will be used to generate the
    ``SDK_URL``.

SCOPE:
    By default, the ``email`` scope is required depending on whether or not
    ``SOCIALACCOUNT_QUERY_EMAIL`` is enabled.
    Apps using permissions beyond ``email`` and ``public_profile``
    require review by Facebook.
    See `Permissions with Facebook Login <https://developers.facebook.com/docs/facebook-login/permissions>`_
    for more information.

AUTH_PARAMS:
    Use ``AUTH_PARAMS`` to pass along other parameters to the ``FB.login``
    JS SDK call.

FIELDS:
    The fields to fetch from the Graph API ``/me/?fields=`` endpoint.
    For example, you could add the ``'friends'`` field in order to
    capture the user's friends that have also logged into your app using
    Facebook (requires ``'user_friends'`` scope).

EXCHANGE_TOKEN:
    The JS SDK returns a short-lived token suitable for client-side use. Set
    ``EXCHANGE_TOKEN = True`` to make a server-side request to upgrade to a
    long-lived token before storing in the ``SocialToken`` record. See
    `Expiration and Extending Tokens <https://developers.facebook.com/docs/facebook-login/access-tokens#extending>`_.

LOCALE_FUNC:
    The locale for the JS SDK is chosen based on the current active language of
    the request, taking a best guess. This can be customized using the
    ``LOCALE_FUNC`` setting, which takes either a callable or a path to a callable.
    This callable must take exactly one argument, the request, and return `a
    valid Facebook locale <http://developers.facebook.com/docs/
    internationalization/>`_ as a string, e.g. US English:

    .. code-block:: python

        SOCIALACCOUNT_PROVIDERS = {
            'facebook': {
                'LOCALE_FUNC': lambda request: 'en_US'
            }
        }

VERIFIED_EMAIL:
    It is not clear from the Facebook documentation whether or not the fact
    that the account is verified implies that the email address is verified
    as well. For example, verification could also be done by phone or credit
    card. To be on the safe side, the default is to treat email addresses
    from Facebook as unverified. But, if you feel that is too paranoid, then
    use this setting to mark them as verified. Due to lack of an official
    statement from the side of Facebook, attempts have been made to
    `reverse engineer the meaning of the verified flag <https://stackoverflow.com/questions/14280535/is-it-possible-to-check-if-an-email-is-confirmed-on-facebook>`_.
    Do know that by setting this to ``True`` you may be introducing a security
    risk.

VERSION:
    The Facebook Graph API version to use. The default is ``v13.0``.

App registration (get your key and secret here)
    A key and secret key can be obtained by
    `creating an app <https://developers.facebook.com/apps>`_.
    After registration you will need to make it available to the public.
    In order to do that your app first has to be
    `reviewed by Facebook <https://developers.facebook.com/docs/apps/review>`_.

Development callback URL
    Leave your App Domains empty and put ``http://localhost:8000`` in the
    section labeled ``Website with Facebook Login``. Note that you'll need to
    add your site's actual domain to this section once it goes live.

For Limited Login, it is exclusively supported via the Headless API's "provider
token" flow.

Pass your Limited Login JWT (obtained from the Facebook iOS SDK) to that
endpoint as an ``id_token``.

Note that Limited Login is purely used for login and does not allow access to
the user's Facebook account - no ``SocialToken`` is created.
