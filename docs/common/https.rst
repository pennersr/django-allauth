HTTPS
=====

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
