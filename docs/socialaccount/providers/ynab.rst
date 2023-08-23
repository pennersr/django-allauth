YNAB
------

App Registration
    https://app.youneedabudget.com/settings/developer

Development callback URL
    http://127.0.0.1:8000/accounts/ynab/login/callback/



Default SCOPE permissions are 'read-only'. If this is the desired functionality, do not add SCOPE entry with ynab app
in SOCIALACCOUNT_PROVIDERS. Otherwise, adding SCOPE and an empty string will give you read / write.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'ynab': {
            'SCOPE': ''
        }
    }
