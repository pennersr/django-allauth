Common Functionality
====================

Sending Email
--------------

Emails sent (e.g. in case of password forgotten or email
confirmation) can be altered by providing your own
templates. Templates are named as follows::

    account/email/email_confirmation_signup_subject.txt
    account/email/email_confirmation_signup_message.txt

    account/email/email_confirmation_subject.txt
    account/email/email_confirmation_message.txt

In case you want to include an HTML representation, add an HTML
template as follows::

    account/email/email_confirmation_signup_message.html

    account/email/email_confirmation_message.html

The project does not contain any HTML email templates out of the box.
When you do provide these yourself, note that both the text and HTML
versions of the message are sent.

If this does not suit your needs, you can hook up your own custom
mechanism by overriding the ``send_mail`` method of the account adapter
(``allauth.account.adapter.DefaultAccountAdapter``).


Templates
---------

``allauth`` ships many templates, viewable in the
`allauth/templates <https://github.com/pennersr/django-allauth/tree/main/allauth/templates>`__
directory.

For instance, the view corresponding to the ``account_login`` URL uses the
template ``account/login.html``. If you create a file with this name in your
code layout, it can override the one shipped with ``allauth``.


Messages
--------

The Django messages framework (``django.contrib.messages``) is used if
it is listed in ``settings.INSTALLED_APPS``.  All messages (as in
``django.contrib.messages``) are configurable by overriding their
respective template. If you want to disable a message, simply override
the message template with a blank one.


Admin
-----

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


HTTPS
-----

This app currently provides no functionality for enforcing views to be
HTTPS only, or switching from HTTP to HTTPS (and back) on demand.
There are third party packages aimed at providing precisely this,
so please use those.

What is provided is the following:

- The protocol to be used for generating links (e.g. password
  forgotten) for emails is configurable by means of the
  ``ACCOUNT_DEFAULT_HTTP_PROTOCOL`` setting.

- Automatically switching to HTTPS is built-in for OAuth providers
  that require this (e.g. Amazon). However, remembering the original
  protocol before the switch and switching back after the login is not
  provided.
