OpenStreetMap
-------------

The builtin OpenStreetMap provider is using the now deprecated OAuth 1.0
protocol.  You can no longer create OAuth 1.0 clients, meaning this provider is
there for legacy reasons only.

In order to make use of the new OSM OAuth 2.0 protocol, you can simply configure an OpenID Connect app.

First, register your client application here: https://www.openstreetmap.org/oauth2/applications

Then, configure the settings (or, setup a ``SocialApp``) using the client ID/secret you received while registering the application:

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "APPS": [
            {
                "provider_id": "openstreetmap",
                "name": "OpenStreetMap",
                "client_id": "<insert-id>",
                "secret": "<insert-secret>",
                "settings": {
                    "server_url": "https://www.openstreetmap.org/.well-known/oauth-authorization-server",
                    "scope": ["openid", "read_prefs"],
                },
            },
        ]
    },
  },


For more information, consult the OpenStreetMap OAuth documentation: https://wiki.openstreetmap.org/wiki/OAuth
