Apple
-----

App registration (create an App ID and then a related Service ID here)
    https://developer.apple.com/account/resources/certificates/list

Private Key registration (be sure to save it)
    https://developer.apple.com/account/resources/authkeys/list

Development callback URL
    http://domain.com/accounts/apple/login/callback/

Add the following configuration to your settings:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        "apple": {
            "APP": {
                # Your service identifier.
                "client_id": "your.service.id",

                # The Key ID (visible in the "View Key Details" page).
                "secret": "KEYID",

                 # Member ID/App ID Prefix -- you can find it below your name
                 # at the top right corner of the page, or it’s your App ID
                 # Prefix in your App ID.
                "key": "MEMAPPIDPREFIX",

                # The certificate you downloaded when generating the key.
                "certificate_key": """-----BEGIN PRIVATE KEY-----
    s3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr
    3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3
    c3ts3cr3t
    -----END PRIVATE KEY-----
    """
            }
        }
    }

Note: Sign In With Apple uses a slight variation of OAuth2, which uses a POST
instead of a GET. Unlike a GET with SameSite=Lax, the session cookie will not
get sent along with a POST. If you encounter 'PermissionDenied' errors during
Apple log in, check that you don't have any 3rd party middleweare that is
generating a new session on this cross-origin POST, as this will prevent the
login process from being able to access the original session after the POST
completes.
