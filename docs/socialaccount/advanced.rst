Advanced Usage
==============


Creating and Populating User instances
--------------------------------------

The following adapter methods can be used to intervene in how User
instances are created and populated with data

- ``allauth.socialaccount.adapter.DefaultSocialAccountAdapter``:

  - ``is_open_for_signup(self, request, socialaccount)``: The default function
    returns that is the same as ``ACCOUNT_ADAPTER`` in ``settings.py``.
    You can override this method by returning ``True``/``False``
    if you want to enable/disable socialaccount signup.

  - ``new_user(self, request, sociallogin)``: Instantiates a new, empty
    ``User``.

  - ``save_user(self, request, sociallogin, form=None)``: Populates and
    saves the ``User`` instance (and related social login data). The
    signup form is not available in case of auto signup.

  - ``populate_user(self, request, sociallogin, data)``: Hook that can
    be used to further populate the user instance
    (``sociallogin.account.user``). Here, ``data`` is a dictionary of
    common user properties (``first_name``, ``last_name``, ``email``,
    ``username``, ``name``) that the provider already extracted for you.


Custom Redirects
----------------

If redirecting to statically configurable URLs (as specified in your
project settings) is not flexible enough, then you can override the
following adapter methods:

- ``allauth.socialaccount.adapter.DefaultSocialAccountAdapter``:

  - ``get_connect_redirect_url(self, request, socialaccount)``


Customizing providers
---------------------

When an existing provider doesn't quite meet your needs, you might find yourself
needing to customize a provider.

This can be achieved by subclassing an existing provider and making your changes
there. Providers are defined as django applications, so typically customizing one
will mean creating a django application in your project.  This application will contain your customized
urls.py, views.py and provider.py files. The behaviour that can be customized is beyond
the scope of this documentation.

.. warning::

    In your ``provider.py`` file, you will need to expose the provider class
    by having a module level attribute called ``provider_classes`` with your custom
    classes in a list. This allows your custom provider to be registered properly
    on the basis of the ``INSTALLED_APPS`` setting.

    Be sure to use a custom id property on your provider class such that its default
    URLs do not clash with the provider you are subclassing.

.. code-block:: python

    class GoogleNoDefaultScopeProvider(GoogleProvider):
        id = 'google_no_scope'

        def get_default_scope(self):
            return []

    provider_classes = [GoogleNoDefaultScopeProvider]


Changing provider scopes
------------------------

Some projects may need more scopes than the default required for authentication purposes.

Scopes can be modified via ``SOCIALACCOUNT_PROVIDERS`` in your project settings.py file.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        '<ProviderNameHere>': {
            'SCOPE': [...]
        }
    }

You need to obtain the default scopes that allauth uses by
looking in ``allauth/socialaccount/providers/<ProviderNameHere>/provider.py``
and look for ``def get_default_scope(self):`` method. Copy those default scopes
into the SCOPE list shown above.

Example of adding calendar.readonly scope to Google scopes::

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': [
                'profile',
                'email',
                'openid',
                'https://www.googleapis.com/auth/calendar.readonly'
            ],
        }
    }
