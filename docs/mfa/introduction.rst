Introduction
============

The ``allauth.mfa`` app contains all functionality related to Multi-Factor
Authentication. It supports:

- TOTP based authentication.

- Authentication by recovery codes.

- Viewing, downloading and regenerating recovery codes.

- WebAuthn based credentials.

- Login using passkeys.


Note that in order to use this functionality you need to install the ``mfa`` extras of the ``django-allauth`` package::

  pip install "django-allauth[mfa]"

Remember to add the app to the ``settings.py`` of your project::

    INSTALLED_APPS = [
        ...
        # The required `allauth` apps...
        'allauth',
        'allauth.account',

        # The MFA app:
        'allauth.mfa',
        ...
    ]

Note that :doc:`WebAuthn support <./webauthn>` is disabled by default.
