Shopify
-------

The Shopify provider requires a ``shop`` parameter to login. For
example, for a shop ``petstore.myshopify.com``, use this::

    /accounts/shopify/login/?shop=petstore

You can create login URLs like these as follows:

.. code-block:: python

    {% provider_login_url "shopify" shop="petstore" %}

For setting up authentication in your app, use this url as your ``App URL``
(if your server runs at localhost:8000)::

    http://localhost:8000/accounts/shopify/login/

And set ``Redirection URL`` to::

    http://localhost:8000/accounts/shopify/login/callback/

**Embedded Apps**

If your Shopify app is embedded you will want to tell allauth to do the required JS (rather than server) redirect.::

    SOCIALACCOUNT_PROVIDERS = {
        'shopify': {
            'IS_EMBEDDED': True,
        }
    }

Note that there is more an embedded app creator must do in order to have a page work as an iFrame within
Shopify (building the x_frame_exempt landing page, handing session expiration, etc...).
However that functionality is outside the scope of django-allauth.

**Online/per-user access mode**
Shopify has two access modes, offline (the default) and online/per-user. Enabling 'online' access will
cause all-auth to tie the logged in Shopify user to the all-auth account (rather than the shop as a whole).::

    SOCIALACCOUNT_PROVIDERS = {
        'shopify': {
            'AUTH_PARAMS': {'grant_options[]': 'per-user'},
        }
    }
