Frontier
--------

The Frontier provider is OAuth2 based.

Client registration
*******************
Frontier Developments switched to OAuth2 based authentication in early 2019.
Before a developer can use the authentication and CAPI (Companion API) service
from Frontier, they must first apply for access.

Go to https://user.frontierstore.net/ and apply for access. Once your application
is approved for access. Under "Developer Zone", you will see a list of authorized
clients granted access. To add access for your client, click on the "Create Client"
button and fill out the form and submit the form.

After creating the client access, click on "View" to reveal your Client ID and
Shared Key. You can also regenerate the key in an event that your shared key is
compromised.

Configuring Django
******************
The app credentials are configured for your Django installation via the admin
interface. Create a new socialapp through ``/admin/socialaccount/socialapp/``.

Fill in the form as follows:

* Provider, "Frontier"
* Name, your pick, suggest "Frontier"
* Client id, is called "Client ID" by Frontier
* Secret key, is called "Shared Key" by Frontier
* Key, is not needed, leave blank.

Optionally, you can specify the scope to use as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
      'frontier': {
        'SCOPE': ['auth', 'capi'],
        'VERIFIED_EMAIL': True
      },
    }
