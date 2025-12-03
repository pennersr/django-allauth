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

Authentication Request's Optional Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`oauth2-authentication-optional-parameters`.
