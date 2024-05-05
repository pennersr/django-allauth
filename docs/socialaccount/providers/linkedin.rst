LinkedIn
--------

LinkedIn has become an OpenID Connect compliant provider, avoiding the need for
a custom OAuth2 implementation. Therefore, the ``linkedin_oauth2`` provider is
now deprecated. You can setup LinkedIn, like any other OpenID Connect provider,
as follows:

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
      "openid_connect": {
          "APPS": [
              {
                  "provider_id": "linkedin",
                  "name": "LinkedIn",
                  "client_id": "<insert-id>",
                  "secret": "<insert-secret>",
                  "settings": {
                      "server_url": "https://www.linkedin.com/oauth",
                  },
              }
          ]
      }
  }


App registration (get your key and secret here)
    https://www.linkedin.com/secure/developer?newapp=
