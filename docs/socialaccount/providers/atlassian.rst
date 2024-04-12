Atlassian
---------

Atlassian OAuth 2.0 (3LO) apps provider.

More info:
    https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/


Enabling OAuth 2.0 (3LO)
************************
Before you can implement OAuth 2.0 (3LO) for your app, you need to enable it for your app using the developer console.

Atlassian developer console
    https://developer.atlassian.com/console/myapps/

1. From any page on developer.atlassian.com, select your profile icon in the top-right corner, and from the dropdown, select Developer console.
2. Select your app from the list (or create one if you don't already have one).
3. Select Authorization in the left menu.
4. Next to OAuth 2.0 (3LO), select Configure.
5. Enter the Callback URL. Ex. ``http://127.0.0.1:8000/accounts/atlassian/login/callback/``
6. Click Save changes.

Note, if you haven't already added an API to your app, you should do this now:

1. Select Permissions in the left menu.
2. Next to the API you want to add, select Add.


Django setup
************
The app credentials are configured for your Django installation via the admin
interface. Create a new socialapp through ``/admin/socialaccount/socialapp/``.

Fill in the form as follows:

* Provider, "Atlassian"
* Name, your pick, suggest "Atlassian"
* Client id, is called "Client ID" by Atlassian
* Secret key, is called "Secret" by Atlassian
* Key, is not needed, leave blank.

Optionally, you can specify the scope to use as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'atlassian': {
            'SCOPE': [
                'read:me',
                'write:jira-work',
            ],
        }
    }

.. note:: By default (if you do not specify ``SCOPE``), ``read:me`` scope is requested.
