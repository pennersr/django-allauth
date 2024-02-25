Authelia
--------

At the time of writing, `Authelia <https://www.authelia.com/>`__ supports OpenID Connect (OIDC) as a beta feature. Detailed information about the available configuration options can be found on their `website <https://www.authelia.com/configuration/identity-providers/open-id-connect/>`__.

As documented at https://www.authelia.com/integration/openid-connect/introduction/ the Well Known Discovery Endpoint that can be used as the server url is ``https://auth.example.com/.well-known/openid-configuration`` where ``https://auth.example.com/`` should be replaced by the specific url of your instance of Authelia.

An example configuration for authelia would look like this::


    SOCIALACCOUNT_PROVIDERS = {
        "openid_connect": {
            "APPS": [
                {
                    "provider_id": "authelia",
                    "name": "Authelia SSO",
                    "client_id": "<insert-id>",
                    "secret": "<insert-secret>",
                    "settings": {
                        "server_url": "https://auth.example.com/.well-known/openid-configuration"
                    }
                }
            ]
        }
    }

Note that the client id and the secret must match the configuration in Authelia for this django-allauth app.
