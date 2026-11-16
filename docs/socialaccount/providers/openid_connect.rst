OpenID Connect
--------------

The OpenID Connect provider provides access to multiple independent OpenID
Connect (sub)providers. You configure these (sub)providers by adding apps to the
configuration of the overall OpenID connect provider. Each app represents a
standalone OpenID Connect provider:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        "openid_connect": {
            # Optional PKCE defaults to False, but may be required by your provider
            # Can be set globally, or per app (settings).
            "OAUTH_PKCE_ENABLED": True,
            "APPS": [
                {
                    "provider_id": "my-server",
                    "name": "My Login Server",
                    "client_id": "your.service.id",
                    "secret": "your.service.secret",
                    "settings": {
                        # When enabled, an additional call to the userinfo
                        # endpoint takes place. The data returned is stored in
                        # `SocialAccount.extra_data`. When disabled, the (decoded) ID
                        # token payload is used instead.
                        "fetch_userinfo": True,
                        "oauth_pkce_enabled": True,
                        "server_url": "https://my.server.example.com",
                        # Optional token endpoint authentication method.
                        # May be one of "client_secret_basic", "client_secret_post"
                        # If omitted, a method from the the server's
                        # token auth methods list is used
                        "token_auth_method": "client_secret_basic",
                        # The field to be used as the account ID.
                        "uid_field": "sub",
                        # Optional overrides for the OpenID Connect
                        # configuration fetched from the server's
                        # .well-known/openid-configuration endpoint.
                        "openid_configuration_overrides": {
                            "token_endpoint": "https://my.server.example.com/custom/token",
                        },
                    },
                },
                {
                    "provider_id": "other-server",
                    "name": "Other Login Server",
                    "client_id": "your.other.service.id",
                    "secret": "your.other.service.secret",
                    "settings": {
                        "server_url": "https://other.server.example.com",
                    },
                },
            ]
        }
    }

This configuration example will create two independent provider instances,
``My Login Server`` and ``Other Login Server``.

The OpenID Connect callback URL for each configured server is at
``/accounts/oidc/{id}/login/callback/`` where ``{id}`` is the configured app's
``provider_id`` value (``my-server`` or ``other-server`` in the above example).


RP-Initiated Logout
^^^^^^^^^^^^^^^^^^^

If the OpenID Provider advertises an ``end_session_endpoint``, logout can be
initiated by posting to ``/accounts/oidc/{id}/logout/``. The user is logged out
locally and redirected to the OpenID Provider. The encoded ID token is passed as
an ``id_token_hint`` when available.

Register ``/accounts/oidc/{id}/logout/callback/`` as a post-logout redirect URI
at the OpenID Provider. An optional local ``next`` URL can be included in the
logout request. It is validated using the normal allauth redirect safety rules.


Back-Channel Logout
^^^^^^^^^^^^^^^^^^^

The OpenID Connect back-channel logout URL for each configured server is at
``/accounts/oidc/{id}/logout/backchannel/``. Configure this URL as the
``backchannel_logout_uri`` at the OpenID Provider.

Back-channel logout requires ``allauth.usersessions`` to be installed so that
the session identified by the logout token can be traced back to a Django
session.

.. note::

    `Section 2.4 of OpenID Connect Back-Channel Logout 1.0
    <https://openid.net/specs/openid-connect-backchannel-1_0.html#LogoutToken>`__
    permits a Logout Token to identify a session using either ``sub`` or
    ``sid``. As there is currently no efficient way of looking up a Django
    session given a ``sid`` only, we always require the ``sub`` claim; ``sid``
    remains optional.

Tokens containing only a ``sub`` claim terminate all tracked sessions for the
linked social account; tokens also containing a ``sid`` claim terminate the
matching OpenID Connect session.


Authentication Request's Optional Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`oauth2-authentication-optional-parameters`.
