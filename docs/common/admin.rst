Admin
=====

The Django admin site (``django.contrib.admin``) does not use Django allauth by
default. Since Django admin provides a custom login view, it does not go through
the normal Django allauth workflow.

.. warning::

    This limitation means that Django allauth features are not applied to the
    Django admin site:

    * ``ACCOUNT_LOGIN_ATTEMPTS_LIMIT`` and ``ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT`` do not
      protect Django’s admin login from being brute forced.
    * Any other custom workflow that overrides the Django allauth adapter's
      login method will not be applied.

An easy workaround for this is to require users to login before going to the
Django admin site's login page (note that the following would need to be applied to
every instance of ``AdminSite``):

.. code-block:: python

    from django.conf import settings
    from django.contrib import admin
    from django.contrib.admin.views.decorators import staff_member_required

    admin.site.login = staff_member_required(
        admin.site.login, login_url=settings.LOGIN_URL
    )
