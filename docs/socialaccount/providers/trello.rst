Trello
------

Register the application at

 https://trello.com/app-key

You get one application key per account.

Save the "Key" to "Client id", the "Secret" to "Secret Key" and "Key" to the "Key"
field.

Verify which scope you need at

 https://developers.trello.com/page/authorization

Need to change the default scope? Add or update the `trello` setting to
`settings.py`

.. code-block:: python

  SOCIALACCOUNT_PROVIDERS = {
      'trello': {
          'AUTH_PARAMS': {
              'scope': 'read,write',
          },
      },
  }
