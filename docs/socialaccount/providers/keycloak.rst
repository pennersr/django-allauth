Keycloak
--------

Starting since version 0.56.0, the builtin Keycloak provider has been removed in
favor of relying on the :doc:`openid_connect` provider as is:

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
      "openid_connect": {
          "APPS": [
              {
                  "provider_id": "keycloak",
                  "name": "Keycloak",
                  "client_id": "<insert-id>",
                  "secret": "<insert-secret>",
                  "settings": {
                      "server_url": "http://keycloak:8080/realms/master/.well-known/openid-configuration",
                  },
              }
          ]
      }
  }

Additional Authorization Request Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`oauth2-authorization-request-parameters`.
