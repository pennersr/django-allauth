Microsoft Graph
-----------------

Microsoft Graph API is the gateway to connect to mail, calendar, contacts,
documents, directory, devices and more.

Apps can be registered (for consumer key and secret) here
    https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

By default, `common` (`organizations` and `consumers`) tenancy is configured
for the login. To restrict it, change the `TENANT` setting as shown below.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'microsoft': {
            'TENANT': 'organizations',
        }
    }
