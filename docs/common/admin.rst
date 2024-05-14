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

An easy workaround for this is to require users to login before going to the Django
admin site's login page. For this workaround the following custom decorator is needed:

.. code-block:: python

  from django.conf import settings
  from django.contrib.admin.views.decorators import staff_member_required
  from django.contrib.auth import REDIRECT_FIELD_NAME
  from django.contrib.auth.decorators import login_required

  def staff_member_required_or_redirect(
      view_func=None,
      redirect_field_name=REDIRECT_FIELD_NAME,
      login_url=settings.LOGIN_URL,
      fail_url=settings.LOGIN_REDIRECT_URL,
  ):
      return login_required(
          staff_member_required(
          view_func, redirect_field_name=None, login_url=fail_url
          ),
          redirect_field_name=redirect_field_name,
          login_url=login_url,
      )

This decorator can then be used to force the allauth login flow in the admin site
(note that the following would need to be applied to every instance of ``AdminSite``).

.. code-block:: python

    from django.conf import settings
    from django.contrib import admin
    from django.contrib.admin.views.decorators import staff_member_required

    admin.site.login = staff_member_required_or_redirect(admin.site.login)

.. note::

  Simply using the standard `staff_member_required` will result in an
  `ERR_TOO_MANY_REDIRECTS` error.
