Introduction
============

Rationale
---------

.. include:: ../../README.rst
    :start-after: .. begin-rationale
    :end-before: .. end-rationale

Features
--------

.. include:: ../../README.rst
    :start-after: .. begin-features
    :end-before: .. end-features


Design
------

This package is internally subdivided into individual Django apps that each
target a specific functional part:

- Functionality related to regular (username and/or email based) accounts is implemented in the ``allauth.account`` app.

- Functionality related to social accounts is implemented in the ``allauth.socialaccount`` app.

- Functionality related to multi-factor authentication is implemented in the ``allauth.mfa`` app.

The documentation is structured according to the subdivision above, where each
functional part is covered by its own chapter.
