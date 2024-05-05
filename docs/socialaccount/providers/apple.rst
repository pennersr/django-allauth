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
            "APPS": [{
                # Your service identifier.
                "client_id": "your.service.id",

                # The Key ID (visible in the "View Key Details" page).
                "secret": "KEYID",

                 # Member ID/App ID Prefix -- you can find it below your name
                 # at the top right corner of the page, or it’s your App ID
                 # Prefix in your App ID.
                "key": "MEMAPPIDPREFIX",

                "settings": {
                    # The certificate you downloaded when generating the key.
                    "certificate_key": """-----BEGIN PRIVATE KEY-----
    s3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr
    3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3cr3ts3
    c3ts3cr3t
    -----END PRIVATE KEY-----
    """
                }
            }]
        }
    }

Apple offers two distinct client IDs: a "Bundle ID" and a "Services ID". When
the flow is started from a mobile iOS device the bundle ID is used, whereas a
web authorization flow uses the services ID as the client ID. If you need to
support both client IDs within one project, add an app entry (over at ``APPS``)
for each client ID. For the app specifying the bundle ID, add the following to
the settings so that this app does not show up on the web::

    "settings": { "hidden": True, ... }


Note: Sign In With Apple uses a slight variation of OAuth2, which uses a POST
instead of a GET. Unlike a GET with SameSite=Lax, the session cookie will not
get sent along with a POST. If you encounter 'PermissionDenied' errors during
Apple log in, check that you don't have any 3rd party middleware that is
generating a new session on this cross-origin POST, as this will prevent the
login process from being able to access the original session after the POST
completes.
