TrainingPeaks
-------------

You need to request an API Partnership to get your OAth credentials:

 https://api.trainingpeaks.com/request-access

Make sure to request scope `athlete:profile` to be able to use OAuth
for user login (default if setting `SCOPE` is omitted).

In development you should only use the sandbox services, which is the
default unless you set `USE_PRODUCTION` to `True`.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'trainingpeaks': {
            'SCOPE': ['athlete:profile'],
            'USE_PRODUCTION': False,
        }
    }

API documentation:

 https://github.com/TrainingPeaks/PartnersAPI/wiki
