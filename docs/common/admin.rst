Admin
=====

The Django admin site (``django.contrib.admin``) does not use Django allauth by
default. Since Django admin provides a custom login view, it does not go through
the normal Django allauth workflow.

.. warning::

    This limitation means that Django allauth features are not applied to the
    Django admin site:

    * The admin login is not protected from being brute forced (``ACCOUNT_RATE_LIMITS``).
    * Two-factor authentication is not enforced.
    * Any other custom workflow that overrides the Django allauth adapter's
      login method will not be applied.

An easy workaround for this is to require users to login before going to the
Django admin site's login page, by adding this to urls.py (note that the following would need to be applied to
every instance of ``AdminSite``):


.. code-block:: python

    from django.contrib import admin
    from allauth.account.decorators import secure_admin_login

    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)
