Providers
=========

Most providers require you to sign up for a so called API client or app,
containing a client ID and API secret. You must add a ``SocialApp``
record per provider via the Django admin containing these app
credentials.

When creating the OAuth app on the side of the provider pay special
attention to the callback URL (sometimes also referred to as redirect
URL). If you do not configure this correctly, you will receive login
failures when attempting to log in, such as::

    An error occurred while attempting to login via your social network account.

Use a callback URL of the form::

    http://example.com/accounts/twitter/login/callback/
    http://example.com/accounts/soundcloud/login/callback/
    ...

For local development, use the following::

    http://127.0.0.1:8000/accounts/twitter/login/callback/


23andMe
-------

App registration (get your key and secret here)
    https://api.23andme.com/dev/

Development callback URL
    http://localhost:8000/accounts/23andme/login/callback/


500px
-----

App registration (get your key and secret here)
    https://500px.com/settings/applications

Development callback URL
    http://localhost:8000/accounts/500px/login/callback/


AgaveAPI
--------

Account Signup
    https://public.agaveapi.co/create_account

App registration
    Run ``client-create`` from the cli: https://bitbucket.org/agaveapi/cli/overview

Development callback URL
    http://localhost:8000/accounts/agave/login/callback/
    *May require https url, even for localhost*

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'agave': {
            'API_URL': 'https://api.tacc.utexas.edu',
        }
    }

In the absense of a specified API_URL, the default Agave tenant is
    https://public.agaveapi.co/

Amazon
------

Amazon requires secure OAuth callback URLs (``redirect_uri``), please
see the section on HTTPS about how this is handled.

App registration (get your key and secret here)
    http://login.amazon.com/manageApps

Development callback URL
    https://example.com/accounts/amazon/login/callback/


Amazon Cognito
--------------

App registration (get your key and secret here)
  1. Go to your https://console.aws.amazon.com/cognito/ and create a Cognito User Pool if you haven't already.
  2. Go to General Settings > App Clients section and create a new App Client if you haven't already. Please make sure you select the option to generate a secret key.
  3. Go to App Integration > App Client Settings section and:

    1. Enable Cognito User Pool as an identity provider.
    2. Set the callback and sign-out URLs. (see next section for development callback URL)
    3. Enable Authorization Code Grant OAuth flow.
    4. Select the OAuth scopes you'd like to allow.

  4. Go to App Integration > Domain Name section and create a domain prefix for your Cognito User Pool.

Development callback URL:
  http://localhost:8000/accounts/amazon-cognito/login/callback/

In addition, you'll need to specify your user pool's domain like so:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'amazon_cognito': {
            'DOMAIN': 'https://<domain-prefix>.auth.us-east-1.amazoncognito.com',
        }
    }

Your domain prefix is the value you specified in step 4 of the app registration process.
If you provided a custom domain such as accounts.example.com provide that instead.

AngelList
---------

App registration (get your key and secret here)
    https://angel.co/api/oauth/clients

Development callback URL
    http://localhost:8000/accounts/angellist/login/callback/


Auth0
-----

App registration (get your key and secret here)
    https://manage.auth0.com/#/clients

Development callback URL
    http://localhost:8000/accounts/auth0/login/callback/


You'll need to specify the base URL for your Auth0 domain:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'auth0': {
            'AUTH0_URL': 'https://your.auth0domain.auth0.com',
        }
    }


Authentiq
---------

Browse to https://www.authentiq.com/developers to get started.

App registration
    https://dashboard.authentiq.com/

Sign in or register with your Authentiq ID (select ``Download the app`` while signing in if you don't have Authentiq ID yet).

Development redirect URL
    http://localhost:8000/accounts/authentiq/login/callback/

While testing you can leave the ``Redirect URIs`` field empty in the dashboard. You can specify what identity details to request via the ``SCOPE`` parameter.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'authentiq': {
          'SCOPE': ['email', 'aq:name']
        }
    }

Valid scopes include: ``email``, ``phone``, ``address``, ``aq:name``, ``aq:location``. The default is to request a user's name, and email address if ``SOCIALACCOUNT_QUERY_EMAIL=True``. You can request and require a verified email address by setting ``SOCIALACCOUNT_EMAIL_VERIFICATION=True`` and ``SOCIALACCOUNT_EMAIL_REQUIRED=True``.

Baidu
-----

The Baidu OAuth2 authentication documentation:
    http://developer.baidu.com/wiki/index.php?title=docs/oauth/refresh
    http://developer.baidu.com/wiki/index.php?title=docs/oauth/rest/file_data_apis_lista


Basecamp
--------

App registration (get your key and secret here)
    https://integrate.37signals.com/

The Basecamp OAuth2 authentication documentation
    https://github.com/basecamp/api/blob/master/sections/authentication.md#oauth-2

Development callback URL
    https://localhost:8000/accounts/basecamp/login/callback/


Battle.net
----------

The Battle.net OAuth2 authentication documentation
    https://develop.battle.net/documentation/guides/using-oauth

Register your app here (Blizzard account required)
    https://develop.battle.net/access/clients/create

Development callback URL
    https://localhost:8000/accounts/battlenet/login/callback/

Note that in order to use battletags as usernames, you are expected to override
either the ``username`` field on your User model, or to pass a custom validator
which will accept the ``#`` character using the ``ACCOUNT_USERNAME_VALIDATORS``
setting. Such a validator is available in
``socialaccount.providers.battlenet.validators.BattletagUsernameValidator``.

The following Battle.net settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'facebook': {
            'SCOPE': ['wow.profile', 'sc2.profile'],
            'REGION': 'us',
        }
    }

SCOPE:
    Scope can be an array of the following options: ``wow.profile`` allows
    access to the user's World of Warcraft characters. ``sc2.profile`` allows
    access to the user's StarCraft 2 profile. The default setting is ``[]``.

REGION:
    Either ``apac``, ``cn``, ``eu``, ``kr``, ``sea``, ``tw`` or ``us``

    Sets the default region to use, can be overriden using query parameters
    in the URL, for example: ``?region=eu``. Defaults to ``us``.

Bitbucket
---------

App registration (get your key and secret here)
    https://bitbucket.org/account/user/{{yourusername}}/oauth-consumers/new

Make sure you select the Account:Read permission.

Development callback URL
    http://127.0.0.1:8000/accounts/bitbucket_oauth2/login/callback/

Note that Bitbucket calls the ``client_id`` *Key* in their user interface.
Don't get confused by that; use the *Key* value for your ``client_id`` field.


Box
---

App registration (get your key and secret here)
    https://app.box.com/developers/services/edit/

Development callback URL
    http://localhost:8000/accounts/box/login/callback/


CERN
----
App registration (get your key and secret here)
    https://sso-management.web.cern.ch/OAuth/RegisterOAuthClient.aspx

CERN OAuth2 Documentation
    https://espace.cern.ch/authentication/CERN%20Authentication/OAuth.aspx


Dataporten
----------
App registration (get your key and secret here)
    https://docs.dataporten.no/docs/gettingstarted/

Development callback URL
    http://localhost:8000/accounts/dataporten/login/callback


daum
----

App registration (get your key and secret here)
    https://developers.daum.net/console

Development callback URL
    http://127.0.0.1:8000/accounts/daum/login/callback/


DigitalOcean
------------

App registration (get your key and secret here)
    https://cloud.digitalocean.com/settings/applications

Development callback URL
    http://127.0.0.1:8000/accounts/digitalocean/login/callback/

With the acquired access token you will have read permissions on the API by
default.  If you also need write access specify the scope as follows.  See
https://developers.digitalocean.com/documentation/oauth/#scopes for details.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'digitalocean': {
            'SCOPE': [
                'read write',
            ],
        }
    }


Discord
-------

App registration and management (get your key and secret here)
    https://discordapp.com/developers/applications/me

Make sure to Add Redirect URI to your application.

Development callback (redirect) URL
    http://127.0.0.1:8000/accounts/discord/login/callback/


Doximity
--------

Doximity OAuth2 implementation documentation
    https://www.doximity.com/developers/documentation#oauth

Request API keys here
    https://www.doximity.com/developers/api_signup

Development callback URL
    http://localhost:8000/accounts/doximity/login/callback/


Draugiem
--------

App registration (get your key and secret here)
    https://www.draugiem.lv/applications/dev/create/?type=4

Authentication documentation
    https://www.draugiem.lv/applications/dev/docs/passport/

Development callback URL
    http://localhost:8000/accounts/draugiem/login/callback/


Dropbox
-------

App registration (get your key and secret here)
    https://www.dropbox.com/developers/apps/

Development callback URL
    http://localhost:8000/accounts/dropbox/login/callback/

Dwolla
------------

App registration (get your key and secret here)
    https://dashboard-uat.dwolla.com/applications

Development callback URL
    http://127.0.0.1:8000/accounts/dwolla/login/callback/


.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'dwolla': {
            'SCOPE': [
                'Send',
                'Transactions',
                'Funding',
                'AccountInfoFull',
            ],
            'ENVIROMENT':'sandbox',
        }
    }


Edmodo
------

Edmodo OAuth2 documentation
    https://developers.edmodo.com/edmodo-connect/edmodo-connect-overview-getting-started/

You can optionally specify additional permissions to use. If no ``SCOPE``
value is set, the Edmodo provider will use ``basic`` by default:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'edmodo': {
            'SCOPE': [
                'basic',
                'read_groups',
                'read_connections',
                'read_user_email',
                'create_messages',
                'write_library_items',
            ]
        }
    }


Eve Online
----------

Register your application at ``https://developers.eveonline.com/applications/create``.
Note that if you have ``STORE_TOKENS`` enabled (the default), you will need to
set up your application to be able to request an OAuth scope. This means you
will need to set it as having "CREST Access". The least obtrusive scope is
"publicData".


Eventbrite
------------------

Log in and click your profile name in the top right navigation, then select
``Account Settings``. Choose ``App Management`` near the bottom of the left
navigation column. You can then click ``Create A New App`` on the upper left
corner.

App registration
    https://www.eventbrite.com/myaccount/apps/

Fill in the form with the following link

Development callback URL
    http://127.0.0.1:8000/accounts/eventbrite/login/callback/

for both the ``Application URL`` and ``OAuth Redirect URI``.


Evernote
--------

Register your OAuth2 application at ``https://dev.evernote.com/doc/articles/authentication.php``:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'evernote': {
            'EVERNOTE_HOSTNAME': 'evernote.com'  # defaults to sandbox.evernote.com
        }
    }


Exist
-----

Register your OAuth2 app in apps page:

    https://exist.io/account/apps/

During development set the callback url to:

    http://localhost:8000/accounts/exist/login/callback/

In production replace localhost with whatever domain you're hosting your app on.

If your app is writing to certain attributes you need to specify this during the
creation of the app.

The following Exist settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'exist': {
            'SCOPE': ['read+write'],
        }
    }

SCOPE:
    The default scope is ``read``. If you'd like to change this set the scope to
    ``read+write``.

For more information:
OAuth documentation: http://developer.exist.io/#oauth2-authentication
API documentation: http://developer.exist.io/


Facebook
--------

For Facebook both OAuth2 and the Facebook Connect Javascript SDK are
supported. You can even mix the two.

An advantage of the Javascript SDK may be a more streamlined user
experience as you do not leave your site. Furthermore, you do not need
to worry about tailoring the login dialog depending on whether or not
you are using a mobile device. Yet, relying on Javascript may not be
everybody's cup of tea.

To initiate a login use:

.. code-block:: python

    {% load socialaccount %}
    {% providers_media_js %}
    <a href="{% provider_login_url "facebook" method="js_sdk" %}">Facebook Connect</a>

or:

.. code-block:: python

    {% load socialaccount %}
    <a href="{% provider_login_url "facebook" method="oauth2" %}">Facebook OAuth2</a>

The following Facebook settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'facebook': {
            'METHOD': 'oauth2',
            'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
            'SCOPE': ['email', 'public_profile', 'user_friends'],
            'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
            'INIT_PARAMS': {'cookie': True},
            'FIELDS': [
                'id',
                'email',
                'name',
                'first_name',
                'last_name',
                'verified',
                'locale',
                'timezone',
                'link',
                'gender',
                'updated_time',
            ],
            'EXCHANGE_TOKEN': True,
            'LOCALE_FUNC': 'path.to.callable',
            'VERIFIED_EMAIL': False,
            'VERSION': 'v2.12',
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
    Apps using permissions beyond ``email``, ``public_profile`` and ``user_friends``
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
    that the account is verified implies that the e-mail address is verified
    as well. For example, verification could also be done by phone or credit
    card. To be on the safe side, the default is to treat e-mail addresses
    from Facebook as unverified. But, if you feel that is too paranoid, then
    use this setting to mark them as verified. Due to lack of an official
    statement from the side of Facebook, attempts have been made to
    `reverse engineer the meaning of the verified flag <https://stackoverflow.com/questions/14280535/is-it-possible-to-check-if-an-email-is-confirmed-on-facebook>`_.
    Do know that by setting this to ``True`` you may be introducing a security
    risk.

VERSION:
    The Facebook Graph API version to use. The default is ``v2.12``.

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


Firefox Accounts
----------------

The Firefox Accounts provider is currently limited to Mozilla relying services
but there is the intention, in the future, to allow third-party services to
delegate authentication. There is no committed timeline for this.

The provider is OAuth2 based. More info:
    https://developer.mozilla.org/en-US/Firefox_Accounts

Note: This is not the same as the Mozilla Persona provider below.

The following Firefox Accounts settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'fxa': {
            'SCOPE': ['profile'],
            'OAUTH_ENDPOINT': 'https://oauth.accounts.firefox.com/v1',
            'PROFILE_ENDPOINT': 'https://profile.accounts.firefox.com/v1',
        }
    }

SCOPE:
    Requested OAuth2 scope. Default is ['profile'], which will work for
    applications on the Mozilla trusted whitelist. If your application is not
    on the whitelist, then define SCOPE to be ['profile:email', 'profile:uid'].

OAUTH_ENDPOINT:
    Explicitly set the OAuth2 endpoint. Default is the production endpoint
    "https://oauth.accounts.firefox.com/v1".

PROFILE_ENDPOINT:
    Explicitly set the profile endpoint. Default is the production endpoint
    and is "https://profile.accounts.firefox.com/v1".


Flickr
------

App registration (get your key and secret here)
    https://www.flickr.com/services/apps/create/

You can optionally specify the application permissions to use. If no ``perms``
value is set, the Flickr provider will use ``read`` by default.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'flickr': {
            'AUTH_PARAMS': {
                'perms': 'write',
            }
        }
    }

More info:
    https://www.flickr.com/services/api/auth.oauth.html#authorization


GitHub
------

App registration (get your key and secret here)
    https://github.com/settings/applications/new

Development callback URL
    http://127.0.0.1:8000/accounts/github/login/callback/

If you want more than just read-only access to public data, specify the scope
as follows. See https://developer.github.com/v3/oauth/#scopes for details.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'github': {
            'SCOPE': [
                'user',
                'repo',
                'read:org',
            ],
        }
    }

Enterprise Support
******************

If you use GitHub Enterprise add your server URL to your Django settings as
follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'github': {
            'GITHUB_URL': 'https://your.github-server.domain',
        }
    }


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
        'gitlab': {
            'GITLAB_URL': 'https://your.gitlab.server.tld',
            'SCOPE': ['api'],
        },
    }


Globus
------

Registering an application:
    https://developers.globus.org/

By default, you will have access to the openid, profile, and offline_access
scopes.  With the offline_access scope, the API will provide you with a
refresh token.  For additional scopes, see the Globus API docs:

 https://docs.globus.org/api/auth/reference/

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'globus': {
            'SCOPE': [
                'openid',
                'profile',
                'email',
                'urn:globus:auth:scope:transfer.api.globus.org:all'
            ]
        }
    }



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
            }
        }
    }

By default, ``profile`` scope is required, and optionally ``email`` scope
depending on whether or not ``SOCIALACCOUNT_QUERY_EMAIL`` is enabled.

You must set ``AUTH_PARAMS['access_type']`` to ``offline`` in order to
receive a refresh token on first login and on reauthentication requests.


Instagram
---------

App registration (get your key and secret here)
    https://www.instagram.com/developer/clients/manage/

Development callback URL
    http://localhost:8000/accounts/instagram/login/callback/


JupyterHub
----------

Documentation on configuring a key and secret key
    https://jupyterhub.readthedocs.io/en/stable/api/services.auth.html

Development callback URL
    http://localhost:800/accounts/jupyterhub/login/callback/

Specify the URL of your JupyterHub server as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'jupyterhub': {
            'API_URL': 'https://jupyterhub.example.com',
        }
    }

Kakao
-----

App registration (get your key here)
    https://developers.kakao.com/apps

Development callback URL
    http://localhost:8000/accounts/kakao/login/callback/


Line
----

App registration (get your key and secret here)
    https://business.line.me

Development callback URL
    http://127.0.0.1:8000/accounts/line/login/callback/


LinkedIn
--------

The LinkedIn provider comes in two flavors: OAuth 1.0
(``allauth.socialaccount.providers.linkedin``) and OAuth 2.0
(``allauth.socialaccount.providers.linkedin_oauth2``).

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

MailChimp (OAuth2)
------------------

MailChimp has a simple API for working with your own data and a `good library`_
already exists for this use. However, to allow other MailChimp users to use an
app you develop, the OAuth2 API allows those users to give or revoke access
without creating a key themselves.

.. _good library: https://pypi.python.org/pypi/mailchimp3

Registering a new app
*********************

Instructions for generating your own OAuth2 app can be found at
https://developer.mailchimp.com/documentation/mailchimp/guides/how-to-use-oauth2/.
It is worth reading that carefully before following the instructions below.

Login via https://login.mailchimp.com/, which will redirect you to
``https://usX.admin.mailchimp.com/`` where the prefix ``usX`` (``X`` is an
integer) is the subdomain you need to connect to. Click on your username in the
top right corner and select *Profile*. On the next page select *Extras* then
click API keys, which should lead you to:

App registration (where ``X`` is dependent on your account)
    https://usX.admin.mailchimp.com/account/oauth2/

Fill in the form with the following URL for local development:

Development callback URL
    https://127.0.0.1:8000/accounts/mailchimp/login/callback/

Testing Locally
***************

Note the requirement of **https**. If you would like to test OAuth2
authentication locally before deploying a default django project will raise
errors because development mode does not support ``https``. One means of
circumventing this is to install ``django-extensions``::

    pip install django-extensions

add it to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_extensions',
        ...
    )

and then run::

    ./manage.py runserver_plus --cert cert

which should allow you to test locally via https://127.0.0.1:8000. Some
browsers may require enabling this on localhost and not support by default and
ask for permission.


Microsoft Graph
-----------------

Microsoft Graph API is the gateway to connect to mail, calendar, contacts,
documents, directory, devices and more.

Apps can be registered (for consumer key and secret) here
    https://apps.dev.microsoft.com/

By default, `common` (`organizations` and `consumers`) tenancy is configured
for the login. To restrict it, change the `tenant` setting as shown below.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'microsoft': {
            'tenant': 'organizations',
        }
    }


Naver
-----

App registration (get your key and secret here)
    https://developers.naver.com/appinfo

Development callback URL
    http://localhost:8000/accounts/naver/login/callback/


NextCloud
---------

The following NextCloud settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'nextcloud': {
            'SERVER': 'https://nextcloud.example.org',
        }
    }


App registration (get your key and secret here)

    https://nextcloud.example.org/settings/admin/security

Odnoklassniki
-------------

App registration (get your key and secret here)
    http://apiok.ru/wiki/pages/viewpage.action?pageId=42476486

Development callback URL
    http://example.com/accounts/odnoklassniki/login/callback/


OpenID
------

The OpenID provider does not require any settings per se. However, a typical
OpenID login page presents the user with a predefined list of OpenID providers
and allows the user to input their own OpenID identity URL in case their
provider is not listed by default. The list of providers displayed by the
builtin templates can be configured as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'openid': {
            'SERVERS': [
                dict(id='yahoo',
                     name='Yahoo',
                     openid_url='http://me.yahoo.com'),
                dict(id='hyves',
                     name='Hyves',
                     openid_url='http://hyves.nl'),
                dict(id='google',
                     name='Google',
                     openid_url='https://www.google.com/accounts/o8/id'),
            ]
        }
    }

You can manually specify extra_data you want to request from server as follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'openid':
            { 'SERVERS':
                 [ dict(id='mojeid',
                      name='MojeId',
                      openid_url='https://mojeid.cz/endpoint/',
                      extra_attributes = [
                          ('phone', 'http://axschema.org/contact/phone/default', False),
                          ('birth_date', 'http://axschema.org/birthDate', False,),
                      ])]}}

Attributes are in form (id, name, required) where id is key in extra_data field of socialaccount,
name is identifier of requested attribute and required specifies whether attribute is required.

If you want to manually include login links yourself, you can use the
following template tag:

.. code-block:: python

    {% load socialaccount %}
    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>

The OpenID provider can be forced to operate in stateless mode as follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'openid':
            { 'SERVERS':
                [ dict(id='steam',
                    name='Steam',
                    openid_url='https://steamcommunity.com/openid',
                    stateless=True,
                )]}}

OpenStreetMap
-------------

Register your client application under `My Settings`/`oauth settings`:

    https://www.openstreetmap.org/user/{Display Name}/oauth_clients

In this page you will get your key and secret

For more information:
OpenStreetMap OAuth documentation: https://wiki.openstreetmap.org/wiki/OAuth


ORCID
-----

The ORCID provider should work out of the box provided that you are using the
Production ORCID registry and the public API. In other settings, you will need
to define the API you are using in your site's settings, as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'orcid': {
            # Base domain of the API. Default value: 'orcid.org', for the production API
            'BASE_DOMAIN':'sandbox.orcid.org',  # for the sandbox API
            # Member API or Public API? Default: False (for the public API)
            'MEMBER_API': True,  # for the member API
        }
    }


Patreon
-------

The following Patreon settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'paypal': {
            'VERSION': 'v1',
            'SCOPE': ['pledges-to-me', 'users', 'my-campaign'],
        }
    }

VERSION:
    API version. Either ``v1`` or ``v2``. Defaults to ``v1``.

SCOPE:
    Defaults to the scope above if using API v1. If using v2, the scope defaults to ``['identity', 'identity[email]', 'campaigns', 'campaigns.members']``.

API documentation:
    https://www.patreon.com/platform/documentation/clients

App registration (get your key and secret for the API here):
    https://www.patreon.com/portal/registration/register-clients

Development callback URL
    http://127.0.0.1:8000/accounts/patreon/login/callback/


Paypal
------

The following Paypal settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'paypal': {
            'SCOPE': ['openid', 'email'],
            'MODE': 'live',
        }
    }

SCOPE:
    In the Paypal developer site, you must also check the required attributes
    for your application. For a full list of scope options, see
    https://developer.paypal.com/docs/integration/direct/identity/attributes/

MODE:
    Either ``live`` or ``test``. Set to test to use the Paypal sandbox.

App registration (get your key and secret here)
    https://developer.paypal.com/webapps/developer/applications/myapps

Development callback URL
    http://example.com/accounts/paypal/login/callback


Persona
-------

Note: Mozilla Persona was shut down on November 30th 2016. See
`the announcement <https://wiki.mozilla.org/Identity/Persona_Shutdown_Guidelines_for_Reliers>`_
for details.

Mozilla Persona requires one setting, the "AUDIENCE" which needs to be the
hardcoded hostname and port of your website. See
https://developer.mozilla.org/en-US/Persona/Security_Considerations#Explicitly_specify_the_audience_parameter
for more information why this needs to be set explicitly and can't be derived
from user provided data:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'persona': {
            'AUDIENCE': 'https://www.example.com',
        }
    }


The optional ``REQUEST_PARAMETERS`` dictionary contains parameters that are
passed as is to the ``navigator.id.request()`` method to influence the
look and feel of the Persona dialog:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'persona': {
            'AUDIENCE': 'https://www.example.com',
            'REQUEST_PARAMETERS': {'siteName': 'Example'},
        }
    }


Pinterest
---------

The Pinterest OAuth2 documentation:

    https://developers.pinterest.com/docs/api/overview/#authentication

You can optionally specify additional permissions to use. If no ``SCOPE``
value is set, the Pinterest provider will use ``read_public`` by default.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'pinterest': {
            'SCOPE': [
                'read_public',
                'read_relationships',
            ]
        }
    }

SCOPE:
    For a full list of scope options, see
    https://developers.pinterest.com/docs/api/overview/#scopes

QuickBooks
----------

App registration (get your key and secret here)
    https://developers.intuit.com/v2/ui#/app/startcreate

Development callback URL
    http://localhost:8000/accounts/quickbooks/login/callback/

You can specify sandbox mode by adding the following to the SOCIALACCOUNT_PROVIDERS in your settings.

You can also add space-delimited scope to utilize the QuickBooks Payments and Payroll API

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'quickbooks': {
            'SANDBOX': TRUE,
            'SCOPE': [
              'openid',
              'com.intuit.quickbooks.accounting com.intuit.quickbooks.payment',
              'profile',
              'phone',
            ]
        }
    }

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






Salesforce
----------

The Salesforce provider requires you to set the login VIP as the provider
model's 'key' (in addition to client id and secret). Production environments
use https://login.salesforce.com/. Sandboxes use https://test.salesforce.com/.

HTTPS is required for the callback.

Development callback URL
    https://localhost:8000/accounts/salesforce/login/callback/

Salesforce OAuth2 documentation
    https://developer.salesforce.com/page/Digging_Deeper_into_OAuth_2.0_on_Force.com

To Use:

- Include allauth.socialaccount.providers.salesforce in INSTALLED_APPS
- In a new Salesforce Developer Org, create a Connected App
  with OAuth (minimum scope id, openid), and a callback URL
- Create a Social application in Django admin, with client id,
  client key, and login_url (in "key" field)

ShareFile
---------

The following ShareFile settings are available.
  https://api.sharefile.com/rest/

SUBDOMAIN:
 Subdomain of your organization with ShareFile.  This is required.

 Example:
      ``test`` for ``https://test.sharefile.com``

APICP:
 Defaults to ``secure``.  Refer to the ShareFile documentation if you
 need to change this value.

DEFAULT_URL:
 Defaults to ``https://secure.sharefile.com``  Refer to the ShareFile
 documentation if you need to change this value.


Example:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
    'sharefile': {
        'SUBDOMAIN': 'TEST',
        'APICP': 'sharefile.com',
        'DEFAULT_URL': 'https://secure.sharefile.com',
                 }
    }

Shopify
-------

The Shopify provider requires a ``shop`` parameter to login. For
example, for a shop ``petstore.myshopify.com``, use this::

    /accounts/shopify/login/?shop=petstore

You can create login URLs like these as follows:

.. code-block:: python

    {% provider_login_url "shopify" shop="petstore" %}

For setting up authentication in your app, use this url as your ``App URL``
(if your server runs at localhost:8000)::

    http://localhost:8000/accounts/shopify/login/

And set ``Redirection URL`` to::

    http://localhost:8000/accounts/shopify/login/callback/

**Embedded Apps**

If your Shopify app is embedded you will want to tell allauth to do the required JS (rather than server) redirect.::

    SOCIALACCOUNT_PROVIDERS = {
        'shopify': {
            'IS_EMBEDDED': True,
        }
    }

Note that there is more an embedded app creator must do in order to have a page work as an iFrame within
Shopify (building the x_frame_exempt landing page, handing session expiration, etc...).
However that functionality is outside the scope of django-allauth.

**Online/per-user access mode**
Shopify has two access modes, offline (the default) and online/per-user. Enabling 'online' access will
cause all-auth to tie the logged in Shopify user to the all-auth account (rather than the shop as a whole).::

    SOCIALACCOUNT_PROVIDERS = {
        'shopify': {
            'AUTH_PARAMS': {'grant_options[]': 'per-user'},
        }
    }


Slack
-----

App registration (get your key and secret here)
    https://api.slack.com/apps/new

Development callback URL
    http://example.com/accounts/slack/login/callback/

API documentation
    https://api.slack.com/docs/sign-in-with-slack


SoundCloud
----------

SoundCloud allows you to choose between OAuth1 and OAuth2. Choose the latter.

App registration (get your key and secret here)
    http://soundcloud.com/you/apps/new

Development callback URL
    http://example.com/accounts/soundcloud/login/callback/


Stack Exchange
--------------

Register your OAuth2 app over at ``http://stackapps.com/apps/oauth/register``.
Do not enable "Client Side Flow". For local development you can simply use
"localhost" for the OAuth domain.

As for all providers, provider specific data is stored in
``SocialAccount.extra_data``. For Stack Exchange we need to choose what data to
store there by choosing the Stack Exchange site (e.g. Stack Overflow, or
Server Fault). This can be controlled by means of the ``SITE`` setting:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'stackexchange': {
            'SITE': 'stackoverflow',
        }
    }


Steam
-----

Steam is an OpenID-compliant provider. However, the `steam` provider allows
access to more of the user's details such as username, full name, avatar, etc.

You need to register an API key here:
    https://steamcommunity.com/dev/apikey

Make sure to create a Steam SocialApp with that secret key.


Strava
------

Register your OAuth2 app in api settings page:

    https://strava.com/settings/api

In this page you will get your key and secret

Development callback URL (only the domain is required on strava.com/settings/api)

    http://example.com/accounts/strava/login/callback/

For more information:
Strava auth documentation: https://developers.strava.com/docs/authentication/
API documentation: https://developers.strava.com/docs/reference/


Stripe
------

You register your OAUth2 app via the Connect->Settings page of the Stripe
dashboard:

 https://dashboard.stripe.com/account/applications/settings

This page will provide you with both a Development and Production `client_id`.

You can also register your OAuth2 app callback on the Settings page in the
"Website URL" box, e.g.:

 http://example.com/accounts/stripe/login/callback/

However, the OAuth2 secret key is not on this page. The secret key is the same
secret key that you use with the Stripe API generally. This can be found on the
Stripe dashboard API page:

 https://dashboard.stripe.com/account/apikeys

See more in documentation
 https://stripe.com/docs/connect/standalone-accounts


Trello
------

Register the application at

 https://trello.com/app-key

You get one application key per account.

Save the "Key" to "Client id", the "Secret" to "Secret Key" and "Key" to the "Key"
field.

Verify which scope you need at

 https://developers.trello.com/page/authorization

Need to change the default scope? Add or update the `trello` setting to
`settings.py`

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
      'trello': {
          'AUTH_PARAMS': {
              'scope': 'read,write',
          },
      },
  }

Twitch
------

App registration (get your key and secret here)
    http://dev.twitch.tv/console

Development callback URL
    http://localhost:8000/accounts/twitch/login/callback/

Twitter
-------

You will need to create a Twitter app and configure the Twitter provider for
your Django application via the admin interface.

App registration
****************

To register an app on Twitter you will need a Twitter account. With an account, you
can create a new app via::

    https://apps.twitter.com/app/new

In the app creation form fill in the development callback URL::

    http://127.0.0.1:8000/accounts/twitter/login/callback/

Twitter won't allow using http://localhost:8000.

For production use a callback URL such as::

   http://{{yourdomain}}.com/accounts/twitter/login/callback/

To allow users to login without authorizing each session, select "Allow this
application to be used to Sign in with Twitter" under the application's
"Settings" tab.

App database configuration through admin
****************************************

The second part of setting up the Twitter provider requires you to configure
your Django application. Configuration is done by creating a Socialapp object
in the admin. Add a social app on the admin page::

    /admin/socialaccount/socialapp/

Use the twitter keys tab of your application to fill in the form. It's located::

    https://apps.twitter.com/app/{{yourappid}}/keys

The configuration is as follows:

* Provider, "Twitter"
* Name, your pick, suggest "Twitter"
* Client id, is called "Consumer Key (API Key)" on Twitter
* Secret key, is called "Consumer Secret (API Secret)" on Twitter
* Key, is not needed, leave blank


Untappd
-------

App registration
****************

    https://untappd.com/api/register?register=new

In the app creation form fill in the development callback URL, e.g.::

    http://127.0.0.1:8000/accounts/untappd/login/callback/

For production, make it your production host, e.g.::

   http://yoursite.com/accounts/untappd/login/callback/

SocialApp configuration
***********************

The configuration values come from your API dashboard on Untappd:

    https://untappd.com/api/dashboard

* Provider: "Untappd"
* Name: "Untappd"
* Client id: "Client ID" from Untappd
* Secret key: "Client Secret" from Untappd
* Sites: choose your site


Telegram
--------

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'telegram': {
            'TOKEN': 'insert-token-received-from-botfather'
        }
    }


Vimeo
-----

App registration (get your key and secret here)
    https://developer.vimeo.com/apps

Development callback URL
    http://localhost:8000/a

Vimeo (OAuth 2)
---------------

App registration (get your key and secret here)
    https://developer.vimeo.com/apps

Development callback URL
    http://localhost:8000/accounts/vimeo_oauth2/login/callback/

VK
--

App registration
    https://vk.com/editapp?act=create

Development callback URL ("Site address")
    http://localhost


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


Weibo
-----

Register your OAuth2 app over at ``http://open.weibo.com/apps``. Unfortunately,
Weibo does not allow for specifying a port number in the authorization
callback URL. So for development purposes you have to use a callback url of
the form ``http://127.0.0.1/accounts/weibo/login/callback/`` and run
``runserver 127.0.0.1:80``.


Weixin
------

The Weixin OAuth2 documentation:

    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419316505&token=&lang=zh_CN

Weixin supports two kinds of oauth2 authorization, one for open platform and
one for media platform, AUTHORIZE_URL is the only difference between them, you
can specify ``AUTHORIZE_URL`` in setting, If no ``AUTHORIZE_URL`` value is set
will support open platform by default, which value is
``https://open.weixin.qq.com/connect/qrconnect``.

You can optionally specify additional scope to use. If no ``SCOPE`` value
is set, will use ``snsapi_login`` by default(for Open Platform Account, need
registration). Other ``SCOPE`` options are: snsapi_base, snsapi_userinfo.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'weixin': {
            'AUTHORIZE_URL': 'https://open.weixin.qq.com/connect/oauth2/authorize',  # for media platform
            'SCOPE': ['snsapi_base'],
        }
    }


Xing
----

App registration (get your key and secret here)
    https://dev.xing.com/applications

Development callback URL
    http://localhost:8000


Yahoo
------

Register your OAuth2 app below and enter the resultant client id and secret into admin
    https://developer.yahoo.com/apps/create/

YNAB
------

App Registration
    https://app.youneedabudget.com/settings/developer

Development callback URL
    http://127.0.0.1:8000/accounts/ynab/login/callback/



Default SCOPE permissions are 'read-only'. If this is the desired functionality, do not add SCOPE entry with ynab app
in SOCIALACCOUNT_PROVIDERS. Otherwise, adding SCOPE and an empty string will give you read / write.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'ynab': {
            'SCOPE': ''
        }
    }
