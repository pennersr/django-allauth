==========================
Welcome to django-allauth!
==========================

.. image:: https://github.com/pennersr/django-allauth/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/pennersr/django-allauth/actions

.. image:: https://img.shields.io/pypi/v/django-allauth.svg
   :target: https://pypi.python.org/pypi/django-allauth

.. image:: https://coveralls.io/repos/pennersr/django-allauth/badge.svg?branch=main
   :alt: Coverage Status
   :target: https://coveralls.io/r/pennersr/django-allauth

.. image:: https://pennersr.github.io/img/bitcoin-badge.svg
   :target: https://blockchain.info/address/1AJXuBMPHkaDCNX2rwAy34bGgs7hmrePEr

.. image:: https://badgen.net/liberapay/receives/pennersr
   :target: https://en.liberapay.com/pennersr

.. image:: https://img.shields.io/badge/code%20style-pep8-green.svg
   :target: https://www.python.org/dev/peps/pep-0008/

.. image:: https://img.shields.io/badge/code_style-standard-brightgreen.svg
   :target: http://standardjs.com

.. image:: https://pennersr.github.io/img/emacs-badge.svg
   :target: https://www.gnu.org/software/emacs/

Integrated set of Django applications addressing authentication,
registration, account management as well as 3rd party (social) account
authentication.

Home page
  http://www.intenct.nl/projects/django-allauth/

Source code
  http://github.com/pennersr/django-allauth

Mailing list
  http://groups.google.com/group/django-allauth

Documentation
  https://django-allauth.readthedocs.io/en/latest/

Stack Overflow
  http://stackoverflow.com/questions/tagged/django-allauth

Rationale
=========

Most existing Django apps that address the problem of social
authentication unfortunately focus only on one dimension - the social. 
Most developers end up integrating another app in order to support authentication 
flows that are locally generated. 

This approach creates a development gap between local and social
authentication flows. It has remained an issue in spite of numerous common 
scenarios that both require. For example, an e-mail address passed along by an
OpenID provider may not be verified. Therefore, prior to hooking up
an OpenID account to a local account the e-mail address must be
verified. This essentially is one of many use cases that mandate e-mail 
verification to be present in both worlds.

Integrating both is a humongous and tedious process. It is not as
simple as adding one social authentication app, and one
local account registration app to your ``INSTALLED_APPS`` list.

This inadequacy is the reason for this project's existence  -- to offer a fully
integrated authentication app that allows for both local and social
authentication, with flows that just work, beautifully !


Commercial Support
==================

This project is sponsored by IntenCT_. If you require assistance on
your project(s), please contact us: info@intenct.nl.

.. _IntenCT: http://www.intenct.info


Cross-Selling
=============

If you like this, you may also like:

- django-trackstats: https://github.com/pennersr/django-trackstats
- netwell: https://github.com/pennersr/netwell
- Shove: https://github.com/pennersr/shove
