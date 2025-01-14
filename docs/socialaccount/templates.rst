Template Tags
=============

Use the ``provider_login_url`` tag to generate provider specific login URLs::

    {% load socialaccount %}

    <a href="{% provider_login_url "openid" openid="https://www.google.com/accounts/o8/id" next="/success/url/" %}">Google</a>
    <a href="{% provider_login_url "twitter" %}">Twitter</a>

Here, you can pass along an optional ``process`` parameter that
indicates how to process the social login. You can choose between
``login`` and ``connect``::

    <a href="{% provider_login_url "twitter" process="connect" %}">Connect a Twitter account</a>

Furthermore, you can pass along an ``action`` parameter with value
``reauthenticate`` to indicate that you want the user to be re-prompted
for authentication even if they already signed in before. For now, this
is supported by Facebook, Google, Twitter, and Discord only.

For Javascript based logins (e.g. when you enable the Facebook JS
SDK), you will need to make sure that the required Javascript is
loaded. The following tag loads all scripts for the enabled
providers::

    {% providers_media_js %}

For easy access to the social accounts for a user use::

    {% get_social_accounts user as accounts %}

Then::

    {{accounts.twitter}} -- a list of connected Twitter accounts
    {{accounts.twitter.0}} -- the first Twitter account
    {% if accounts %} -- if there is at least one social account


Finally, social authentication providers configured for the current site
can be retrieved via::

    {% get_providers as socialaccount_providers %}

Which will populate the ``socialaccount_providers`` variable in the
template context with a list of configured social authentication
providers. This supersedes the context processor used in version 0.21 and
below.
