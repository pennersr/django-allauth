LemonLDAP::NG
-------------

Create a new OpenID Connect Relying Party with the following settings:

* Exported attributes:

    * ``email``
    * ``name``
    * ``preferred_username``

* Basic options:

    * Development Redirect URI: http://localhost:8000/accounts/lemonldap/login/callback/

The following LemonLDAP::NG settings are available.

LEMONLDAP_URL:
    The base URL of your LemonLDAP::NG portal. For example: ``https://auth.example.com``

Example:

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
      'lemonldap': {
          'LEMONLDAP_URL': 'https://auth.example.com'
      }
  }
