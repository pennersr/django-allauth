JupyterHub
----------

Documentation on configuring a key and secret key
    https://jupyterhub.readthedocs.io/en/stable/api/services.auth.html

Development callback URL
    http://localhost:800/accounts/jupyterhub/login/callback/

Specify the URL of your JupyterHub server as follows:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'jupyterhub': {
            'API_URL': 'https://jupyterhub.example.com',
        }
    }
