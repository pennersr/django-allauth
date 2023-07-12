Paypal
------

The following Paypal settings are available:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'paypal': {
            'SCOPE': ['openid', 'email'],
            'MODE': 'live',
        }
    }

SCOPE:
    In the Paypal developer site, you must also check the required attributes
    for your application. For a full list of scope options, see
    https://developer.paypal.com/docs/integration/direct/identity/attributes/

MODE:
    Either ``live`` or ``test``. Set to test to use the Paypal sandbox.

App registration (get your key and secret here)
    https://developer.paypal.com/webapps/developer/applications/myapps

Development callback URL
    http://example.com/accounts/paypal/login/callback
