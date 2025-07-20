Microsoft
---------

.. _ms-graph:

Microsoft Graph
^^^^^^^^^^^^^^^


Microsoft Graph API is the gateway to connect to mail, calendar, contacts,
documents, directory, devices and more.

Apps can be registered (for consumer key and secret) here
    https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

By default, ``common`` (``organizations`` and ``consumers``) tenancy is configured
for the login. To restrict it, change the ``tenant`` setting as shown below.

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
      "microsoft": {
          "APPS": [
              {
                  "client_id": "<insert-id>",
                  "secret": "<insert-secret>",
                  "settings": {
                      "tenant": "organizations",
                      # Optional: override URLs (use base URLs without path)
                      "login_url": "https://login.microsoftonline.com",
                      "graph_url": "https://graph.microsoft.com",
                  }
              }
          ]
      }
  }

.. note:: When you have configured your application to use single tenant authentication make sure to use the fragment above to set the ``"tenant"`` value to ``"organizations"`` in order to prevent the following error:

   .. error:: AADSTS50194: Application 'application id' (application name) is not configured as a multi-tenant application. Usage of the /common endpoint is not supported for such applications created after '10/15/2018'. Use a tenant-specific endpoint or configure the application to be multi-tenant.


Microsoft Azure Entra (OpenID Connect)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For single instances of Microsoft Azure Entra, you should follow the
instructions at :ref:`ms-graph`.

If you want to use Microsoft Azure Entra as an OpenID Connect provider, e.g. to
support multiple Entra instances, follow the OpenID Connect provider
instructions, and configure the following in the settings:

.. code-block:: python

    {
        "server_url": "https://login.microsoftonline.com/common/v2.0",
        "token_auth_method": "client_secret_basic"
    }

- Make sure you change the ``common`` to your tenant id if you are using a single tenant.
- Make sure you added the ``v2.0`` to the end of the URL. Otherwise the email address won't be passed back.
