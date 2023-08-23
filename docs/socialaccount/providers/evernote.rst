Evernote
--------

Register your OAuth2 application at ``https://dev.evernote.com/doc/articles/authentication.php``:

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'evernote': {
            'EVERNOTE_HOSTNAME': 'evernote.com'  # defaults to sandbox.evernote.com
        }
    }
