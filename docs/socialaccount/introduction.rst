Introduction
============

A social account is a user account where authentication is delegated to an external identity provider. The ``allauth.socialaccount`` app is responsible for managing social accounts. It supports:

- Connecting more one or more social accounts to a local/regular account

- Disconnecting a social account -- requires setting a password if
  only the local account remains

- Optional instant-signup for social accounts -- no questions asked
