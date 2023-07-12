Untappd
-------

App registration
****************

    https://untappd.com/api/register?register=new

In the app creation form fill in the development callback URL, e.g.::

    http://127.0.0.1:8000/accounts/untappd/login/callback/

For production, make it your production host, e.g.::

   http://yoursite.com/accounts/untappd/login/callback/

SocialApp configuration
***********************

The configuration values come from your API dashboard on Untappd:

    https://untappd.com/api/dashboard

* Provider: "Untappd"
* Name: "Untappd"
* Client id: "Client ID" from Untappd
* Secret key: "Client Secret" from Untappd
* Sites: choose your site

In addition, you should override your user agent to comply with Untappd's API
rules, and specify something in the format
``<platform>:<app ID>:<version string>``. Otherwise,
you will risk additional rate limiting in your application.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'untappd': {
            'USER_AGENT': 'django:myappid:1.0',
        }
    }
