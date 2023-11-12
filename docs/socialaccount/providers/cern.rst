CERN
----

Starting from September 1st 2023, CERN upgraded their SSO to a standard OpenID
Connect based solution. As a result, the previously builtin CERN provider is no
longer needed and has been removed. Instead, use the regular OpenID Connect
configuration::

    SOCIALACCOUNT_PROVIDERS = {
        "openid_connect": {
            "APPS": [
                {
                    "provider_id": "cern",
                    "name": "CERN",
                    "client_id": "<insert-id>",
                    "secret": "<insert-secret>",
                    "settings": {
                        "server_url": "https://auth.cern.ch/auth/realms/cern/.well-known/openid-configuration",
                    },
                }
            ]
        }
    }

App registration (get your key and secret here)
    https://sso-management.web.cern.ch/OAuth/RegisterOAuthClient.aspx

CERN OAuth2 Documentation
    https://espace.cern.ch/authentication/CERN%20Authentication/OAuth.aspx
