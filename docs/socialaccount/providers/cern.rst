CERN
----

Members of the scientific commmunity affiliated with CERN (https://home.cern/about)
can put their applications behind CERN SSO, which supports OIDC and SAML protocols.
For OIDC, use the regular OpenID Connect configuration:

    SOCIALACCOUNT_PROVIDERS = {
        "openid_connect": {
            "APPS": [
                {
                    "provider_id": "cern",
                    "name": "CERN",
                    "client_id": "<insert-id>",
                    "secret": "<insert-secret>",
                    "settings": {
                        "server_url": "https://auth.cern.ch/auth/realms/cern/.well-known/openid-configuration"
                    }
                }
            ]
        }
    }

App registration (get your key and secret here)
    https://application-portal.web.cern.ch/

Documentation
    https://auth.docs.cern.ch/applications/application-configuration/
