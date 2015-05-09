Providers
=========

Most providers require you to sign up for a so called API client or
app, containing a client ID and API secret. You must add a `SocialApp`
record per provider via the Django admin containing these app
credentials.

When creating the OAuth app on the side of the provider pay special
attention to the callback URL (sometimes also referred to as redirect
URL). If you do not configure this correctly, you will receive login
failures when attempting to log in, such as::

    An error occured while attempting to login via your social network account.

Use a callback URL of the form::

    http://example.com/accounts/twitter/login/callback/
    http://example.com/accounts/soundcloud/login/callback/
    ...

For local development, use the following::

    http://127.0.0.1:8000/accounts/twitter/login/callback/



Amazon
------

Amazon requires secure OAuth callback URLs (`redirect_uri`), please
see the section on HTTPS about how this is handled.

App registration (get your key and secret here)
    http://login.amazon.com/manageApps

Development callback URL
    https://example.com/amazon/login/callback/

AngelList
---------

Register your OAuth app here: https://angel.co/api/oauth/clients

For local development, use the following callback URL::

    http://localhost:8000/accounts/angellist/login/callback/


Facebook
--------

For Facebook both OAuth2 and the Facebook Connect Javascript SDK are
supported. You can even mix the two.

Advantage of the Javascript SDK may be a more streamlined user
experience as you do not leave your site. Furthermore, you do not need
to worry about tailoring the login dialog depending on whether or not
you are using a mobile device. Yet, relying on Javascript may not be
everybody's cup of tea.

To initiate a login use::

    {% load socialaccount %}
    {% providers_media_js %}
    <a href="{% provider_login_url "facebook" method="js_sdk" %}">Facebook Connect</a>

or::

    {% load socialaccount %}
    <a href="{% provider_login_url "facebook" method="oauth2" %}">Facebook OAuth2</a>

The following Facebook settings are available::

    SOCIALACCOUNT_PROVIDERS = \
        {'facebook':
           {'SCOPE': ['email', 'public_profile', 'user_friends'],
            'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
            'METHOD': 'oauth2',
            'LOCALE_FUNC': 'path.to.callable',
            'VERIFIED_EMAIL': False,
            'VERSION': 'v2.3'}}

METHOD:
    Either `js_sdk` or `oauth2`

SCOPE:
    By default, `email` scope is required depending whether or not
    `SOCIALACCOUNT_QUERY_EMAIL` is enabled.
    Except permissions for `email`, `public_profile` and `user_friends`, apps using other permissions require review by Facebook.
    You can look at `Permissions with Facebook Login <https://developers.facebook.com/docs/facebook-login/permissions>`_.

AUTH_PARAMS:
    Use `AUTH_PARAMS` to pass along other parameters to the `FB.login`
    JS SDK call.

LOCALE_FUNC:
    The locale for the JS SDK is chosen based on the current active language of
    the request, taking a best guess. This can be customized using the
    `LOCALE_FUNC` setting, which takes either a callable or a path to a callable.
    This callable must take exactly one argument, the request, and return `a
    valid Facebook locale <http://developers.facebook.com/docs/
    internationalization/>`_ as a string::

        SOCIALACCOUNT_PROVIDERS = \
            { 'facebook':
                { 'LOCALE_FUNC': lambda request: 'zh_CN'} }

VERIFIED_EMAIL:
    It is not clear from the Facebook documentation whether or not the
    fact that the account is verified implies that the e-mail address
    is verified as well. For example, verification could also be done
    by phone or credit card. To be on the safe side, the default is to
    treat e-mail addresses from Facebook as unverified. But, if you
    feel that is too paranoid, then use this setting to mark them as
    verified. Do know that by setting this to `True` you are
    introducing a security risk.

VERSION:
    The Facebook Graph API version to use.

App registration (get your key and secret here)
    A key and secret key can be obtained by creating an app
    https://developers.facebook.com/apps .
    After registration you will need to make it available to the public.
    In order to do that your app first has to be reviewed by Facebook, see
    https://developers.facebook.com/docs/apps/review.

Development callback URL
    Leave your App Domains empty and put in the section `Website with Facebook
    Login` put this as your Site URL: `http://localhost:8000`


Firefox Accounts
----------------

The Firefox Accounts provider is currently limited to Mozilla relying services
but there is the intention to, in the future, allow third-party services to
delegate authentication. There is no committed timeline for this.

The provider is OAuth2 based. More info:
    https://developer.mozilla.org/en-US/Firefox_Accounts

Note: This is not the same as the Mozilla Persona provider below.

GitHub
------

App registration
    https://github.com/settings/applications/new


Google
------

The Google provider is OAuth2 based. More info:
`http://code.google.com/apis/accounts/docs/OAuth2.html#Registering`.


App registration
****************
Create a google app to obtain a key and secret through the developer console:
        https://console.developers.google.com/

After you create a project you will have to create a "Client ID" and fill in some project details for the consent form that will be presented to the client.

Under "APIs & auth" go to "Credentials" and create a new Client ID. Probably you will want a "Web application" Client ID. Provide your domain name or test domain name in "Authorized JavaScript origins". Finally fill in "http://127.0.0.1:8000/accounts/google/login/callback/" in the "Authorized redirect URI" field. You can fill multiple URLs, one for each test domain.After creating the Client ID you will find all details for the Django configuration on this page.

Users that login using the app will be presented a consent form. For this to work additional information is required. Under "APIs & auth" go to "Consent screen" and atleast provide an email and product name.


Django configuration
********************
The app credentials are configured for your Django installation via the admin interface. Create a new socialapp through `/admin/socialaccount/socialapp/`.

Fill in the form as follows:

* Provider, "Google"
* Name, your pick, suggest "Google"
* Client id, is called "Client ID" by Google
* Secret key, is called "Client secret" by Google
* Key, is not needed, leave blank.


Optionally, you can specify the scope to use as follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'google':
            { 'SCOPE': ['profile', 'email'],
              'AUTH_PARAMS': { 'access_type': 'online' } }}

By default, `profile` scope is required, and optionally `email` scope
depending on whether or not `SOCIALACCOUNT_QUERY_EMAIL` is enabled.


LinkedIn
--------

The LinkedIn provider comes in two flavors: OAuth 1.0
(`allauth.socialaccount.providers.linkedin`) and OAuth 2.0
(`allauth.socialaccount.providers.linkedin_oauth2`).

You can specify the scope and fields to fetch as follows::

    SOCIALACCOUNT_PROVIDERS = \
        {'linkedin':
          {'SCOPE': ['r_emailaddress'],
           'PROFILE_FIELDS': ['id',
                             'first-name',
                             'last-name',
                             'email-address',
                             'picture-url',
                             'public-profile-url']}}

By default, `r_emailaddress` scope is required depending on whether or
not `SOCIALACCOUNT_QUERY_EMAIL` is enabled.

Note: if you are experiencing issues where it seems as if the scope
has no effect you may be using an old LinkedIn app that is not
scope enabled. Please refer to
`https://developer.linkedin.com/forum/when-will-old-apps-have-scope-parameter-enabled`
for more background information.

Furthermore, we have experienced trouble upgrading from OAuth 1.0 to
OAuth 2.0 using the same app. Attempting to do so resulted in a weird
error message when fetching the access token::

    missing required parameters, includes an invalid parameter value, parameter more then once. : Unable to retrieve access token : authorization code not found

App registration (get your key and secret here)
        https://www.linkedin.com/secure/developer?newapp=
Development callback URL
        Leave the OAuth redirect URL empty.


Odnoklassniki
-------------

Register your OAuth2 app here: http://apiok.ru/wiki/pages/viewpage.action?pageId=42476486

Development callback URL
    http://example.com/accounts/odnoklassniki/login/callback/


OpenID
------

The OpenID provider does not require any settings per se. However, a
typical OpenID login page presents the user with a predefined list of
OpenID providers and allows the user to input their own OpenID identity
URL in case their provider is not listed by default. The list of
providers displayed by the builtin templates can be configured as
follows::

    SOCIALACCOUNT_PROVIDERS = \
        { 'openid':
            { 'SERVERS':
                [dict(id='yahoo',
                      name='Yahoo',
                      openid_url='http://me.yahoo.com'),
                 dict(id='hyves',
                      name='Hyves',
                      openid_url='http://hyves.nl'),
                 dict(id='google',
                      name='Google',
                      openid_url='https://www.google.com/accounts/o8/id')]}}


If you want to manually include login links yourself, you can use the
following template tag::

    {% load socialaccount %}
    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>

Paypal
------

The following Paypal settings are available::

    SOCIALACCOUNT_PROVIDERS = \
        {'paypal':
           {'SCOPE': ['openid', 'email'],
            'MODE': 'live'}}


SCOPE

In the Paypal developer site, you must also check the required attributes for your application.
For a full list of scope options, see https://developer.paypal.com/docs/integration/direct/identity/attributes/

MODE

Either `live` or `test`. Set to test to use the Paypal sandbox.

App registration (get your key and secret here)
    https://developer.paypal.com/webapps/developer/applications/myapps

Development callback URL
    http://example.com/paypal/login/callback


Persona
-------

Mozilla Persona requires one setting, the "AUDIENCE" which needs to be the
hardcoded hostname and port of your website. See https://developer.mozilla.org/en-US/Persona/Security_Considerations#Explicitly_specify_the_audience_parameter for more
information why this needs to be set explicitely and can't be derived from
user provided data::

    SOCIALACCOUNT_PROVIDERS = \
        { 'persona':
            { 'AUDIENCE': 'https://www.example.com' } }


The optional `REQUEST_PARAMETERS` dictionary contains parameters that are
passed as is to the `navigator.id.request()` method to influence the
look and feel of the Persona dialog::

    SOCIALACCOUNT_PROVIDERS = \
        { 'persona':
            { 'AUDIENCE': 'https://www.example.com',
              'REQUEST_PARAMETERS': {'siteName': 'Example' } } }


SoundCloud
----------

SoundCloud allows you to choose between OAuth1 and OAuth2.  Choose the
latter.

Development callback URL
    http://example.com/accounts/soundcloud/login/callback/

Evernote
----------

Register your OAuth2 application at `https://dev.evernote.com/doc/articles/authentication.php`.

    SOCIALACCOUNT_PROVIDERS = {
        'evernote': {
            'EVERNOTE_HOSTNAME': 'evernote.com'  # defaults to sandbox.evernote.com
        }
    }


Stack Exchange
--------------

Register your OAuth2 app over at
`http://stackapps.com/apps/oauth/register`.  Do not enable "Client
Side Flow". For local development you can simply use "localhost" for
the OAuth domain.

As for all providers, provider specific data is stored in
`SocialAccount.extra_data`. For Stack Exchange we need to choose what
data to store there by choosing the Stack Exchange site (e.g. Stack
Overflow, or Server Fault). This can be controlled by means of the
`SITE` setting::

    SOCIALACCOUNT_PROVIDERS = \
        { 'stackexchange':
            { 'SITE': 'stackoverflow' } }


Twitch
------
Register your OAuth2 app over at
`http://www.twitch.tv/kraken/oauth2/clients/new`.

Twitter
-------

You will need to create a Twitter app and configure the Twitter provider for your Django application via the admin interface.

App registration
****************

To register an app on Twitter you will need a Twitter account after which you can create a new app via::

    https://apps.twitter.com/app/new

In the app creation form fill in the development callback URL::

    http://127.0.0.1:8000

Twitter won't allow using http://localhost:8000.

For production use a callback URL such as::

   http://{{yourdomain}}.com
   
To allow user's to login without authorizing each session select "Allow this application to be used to Sign in with Twitter" under the application's "Settings" tab.

App database configuration through admin
****************************************

The second part of setting up the Twitter provider requires you to configure your Django application.
Configuration is done by creating a Socialapp object in the admin.
Add a social app on the admin page::

    /admin/socialaccount/socialapp/


Use the twitter keys tab of your application to fill in the form. It's located::

    https://apps.twitter.com/app/{{yourappid}}/keys

The configuration is as follows:

* Provider, "Twitter"
* Name, your pick, suggest "Twitter"
* Client id, is called "Consumer Key (API Key)" on Twitter
* Secret key, is called "Consumer Secret (API Secret)" on Twitter
* Key, is not needed, leave blank


Vimeo
-----

App registration
    https://developer.vimeo.com/apps

Development callback URL
    http://localhost:8000


VK
--

App registration
    http://vk.com/apps?act=settings

Development callback URL ("Site address")
    http://localhost


Windows Live
------------

The Windows Live provider currently does not use any settings in
`SOCIALACCOUNT_PROVIDERS`.

App registration (get your key and secret here)
        https://account.live.com/developers/applications/index


Weibo
-----

Register your OAuth2 app over at
`http://open.weibo.com/apps`. Unfortunately, Weibo does not allow for
specifying a port number in the authorization callback URL. So for
development purposes you have to use a callback url of the form
`http://127.0.0.1/accounts/weibo/login/callback/` and run `runserver
127.0.0.1:80`.


Xing
----

App registration
    https://dev.xing.com/applications

Development callback URL
    http://localhost:8000
