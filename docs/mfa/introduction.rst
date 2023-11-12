Introduction
============

The ``allauth.mfa`` app contains all functionality related to Multi-Factor
Authentication. It supports:

- TOTP based authentication.

- Authentication by recovery codes.

- Viewing, downloading and regenerating recovery codes.

Note that in order to use this functionality you need to install the ``mfa`` extras of the ``django-allauth`` package::

  pip install django-allauth[mfa]
