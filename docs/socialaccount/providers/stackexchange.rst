Stack Exchange
--------------

Register your OAuth2 app over at ``http://stackapps.com/apps/oauth/register``.
Do not enable "Client Side Flow". For local development you can simply use
"localhost" for the OAuth domain.

As for all providers, provider specific data is stored in
``SocialAccount.extra_data``. For Stack Exchange we need to choose what data to
store there by choosing the Stack Exchange site (e.g. Stack Overflow, or
Server Fault). This can be controlled by means of the ``SITE`` setting:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'stackexchange': {
            'SITE': 'stackoverflow',
        }
    }
