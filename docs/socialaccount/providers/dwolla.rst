Dwolla
------------

App registration (get your key and secret here)
    https://dashboard-uat.dwolla.com/applications

Development callback URL
    http://127.0.0.1:8000/accounts/dwolla/login/callback/


.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'dwolla': {
            'SCOPE': [
                'Send',
                'Transactions',
                'Funding',
                'AccountInfoFull',
            ],
            'ENVIROMENT':'sandbox',
        }
    }
