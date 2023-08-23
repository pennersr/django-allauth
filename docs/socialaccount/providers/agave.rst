AgaveAPI
--------

Account Signup
    https://public.agaveapi.co/create_account

App registration
    Run ``client-create`` from the cli: https://bitbucket.org/agaveapi/cli/overview

Development callback URL
    http://localhost:8000/accounts/agave/login/callback/
    *May require https url, even for localhost*

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'agave': {
            'API_URL': 'https://api.tacc.utexas.edu',
        }
    }

In the absence of a specified API_URL, the default Agave tenant is
    https://public.agaveapi.co/
