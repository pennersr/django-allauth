Keycloak
--------

Creating a client application
    https://www.keycloak.org/docs/latest/authorization_services/#_resource_server_create_client

Development callback URL
    http://localhost:8000/accounts/keycloak/login/callback/

The following Keycloak settings are available.

KEYCLOAK_URL:
    The url of your hosted keycloak server. For example, you can use: ``https://your.keycloak.server``

KEYCLOAK_URL_ALT:
    An alternate url of your hosted keycloak server. For example, you can use: ``https://your.keycloak.server``

    This can be used when working with Docker on localhost, with a frontend and a backend hosted in different containers.

KEYCLOAK_REALM:
    The name of the ``realm`` you want to use.

Example:

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
      'keycloak': {
          'KEYCLOAK_URL': 'https://keycloak.custom/auth',
          'KEYCLOAK_REALM': 'master'
      }
  }
