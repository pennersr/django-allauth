Decorators
==========

Verified E-mail Required
------------------------

Even when email verification is not mandatory during signup, there
may be circumstances during which you really want to prevent
unverified users to proceed. For this purpose you can use the
following decorator::

    from allauth.account.decorators import verified_email_required

    @verified_email_required
    def verified_users_only_view(request):
        ...

The behavior is as follows:

- If the user isn't logged in, it acts identical to the
  `login_required` decorator.

- If the user is logged in but has no verified e-mail address, an
  e-mail verification mail is automatically resent and the user is
  presented with a page informing them they need to verify their email
  address.
