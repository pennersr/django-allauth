QuickBooks
----------

App registration (get your key and secret here)
    https://developers.intuit.com/v2/ui#/app/startcreate

Development callback URL
    http://localhost:8000/accounts/quickbooks/login/callback/

You can specify sandbox mode by adding the following to the SOCIALACCOUNT_PROVIDERS in your settings.

You can also add space-delimited scope to utilize the QuickBooks Payments and Payroll API

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'quickbooks': {
            'SANDBOX': TRUE,
            'SCOPE': [
              'openid',
              'com.intuit.quickbooks.accounting com.intuit.quickbooks.payment',
              'profile',
              'phone',
            ]
        }
    }
