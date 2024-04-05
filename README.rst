==========================
Welcome to django-allauth!
==========================

.. image:: https://img.shields.io/github/actions/workflow/status/pennersr/django-allauth/ci.yml.png
   :target: https://github.com/pennersr/django-allauth/actions
.. image:: https://img.shields.io/pypi/v/django-allauth.png
   :target: https://pypi.python.org/pypi/django-allauth
.. image:: https://coveralls.io/repos/pennersr/django-allauth/badge.png?branch=main
   :alt: Coverage Status
   :target: https://coveralls.io/r/pennersr/django-allauth
.. image:: https://img.shields.io/badge/bitcoin-donate-yellow.png
   :target: https://blockchain.info/address/1AJXuBMPHkaDCNX2rwAy34bGgs7hmrePEr
.. image:: https://img.shields.io/liberapay/receives/pennersr.png
   :target: https://en.liberapay.com/pennersr
.. image:: https://img.shields.io/badge/code%20style-pep8-green.png
   :target: https://www.python.org/dev/peps/pep-0008/
.. image:: https://img.shields.io/badge/code_style-standard-brightgreen.png
   :target: http://standardjs.com
.. image:: https://img.shields.io/badge/editor-emacs-purple.png
   :target: https://www.gnu.org/software/emacs/
.. image:: https://img.shields.io/weblate/progress/django-allauth.png
   :target: https://hosted.weblate.org/engage/django-allauth/
.. image:: https://img.shields.io/pypi/dm/django-allauth.png
   :target: https://pypistats.org/packages/django-allauth
   :alt: PyPI - Downloads
.. image:: https://img.shields.io/badge/%E2%96%B6%20demo-Django%20project-red.png
   :target: https://django.demo.allauth.org/
   :alt: View Django Demo
.. image:: https://img.shields.io/badge/%E2%96%B6%20demo-React%20SPA-red.png
   :target: https://react.demo.allauth.org/
   :alt: View React SPA Demo

Integrated set of Django applications addressing authentication,
registration, account management as well as 3rd party (social) account
authentication.

Home page
  https://allauth.org/

Source code
  http://github.com/pennersr/django-allauth

Mailing list
  http://groups.google.com/group/django-allauth

Documentation
  https://docs.allauth.org/en/latest/

Stack Overflow
  http://stackoverflow.com/questions/tagged/django-allauth

Demo
  https://django.demo.allauth.org

.. end-welcome

Rationale
=========

.. begin-rationale

Most existing Django apps that address the problem of social
authentication unfortunately focus only on one dimension - the social.
Most developers end up integrating another app in order to support authentication
flows that are locally generated.

This approach creates a development gap between local and social
authentication flows. It has remained an issue in spite of numerous common
scenarios that both require. For example, an email address passed along by an
OpenID provider may not be verified. Therefore, prior to hooking up
an OpenID account to a local account the email address must be
verified. This essentially is one of many use cases that mandate email
verification to be present in both worlds.

Integrating both is a humongous and tedious process. It is not as
simple as adding one social authentication app, and one
local account registration app to your ``INSTALLED_APPS`` list.

This inadequacy is the reason for this project's existence  -- to offer a fully
integrated authentication app that allows for both local and social
authentication, with flows that just work, beautifully !

.. end-rationale


Features
========

.. begin-features

**🔑 Comprehensive account functionality**
    Supports multiple authentication
    schemes (e.g. login by user name, or by email), as well as multiple
    strategies for account verification (ranging from none to mandatory email
    verification).

**👥 Social Login**
    Login using external identity providers, supporting any *Open ID Connect
    compatible* provider, many *OAuth 1.0/2.0* providers, as well as
    custom protocols such as, for example, *Telegram* authentication.

**💼 Enterprise ready**
    Supports SAML 2.0, which is often used in a B2B context.

**🕵️ Battle-tested**
    The package has been out in the open since 2010. It is in use by many
    commercial companies whose business depends on it and has hence been
    subjected to various penetration testing attempts.

**⏳Rate limiting**
    When you expose an authentication-enabled web service to
    the internet, it is important to be prepared for potential brute force
    attempts. Therefore, rate limiting is enabled out of the box.

**🔒 Private**
    Many sites leak information. For example, on many sites you can
    check whether someone you know has an account by input their email address
    into the password forgotten form, or trying to signup with it. We offer
    account enumeration prevention, making it impossible to tell whether or not
    somebody already has an account.

**🧩 Customizable**
    As a developer, you have the flexibility to customize the core functionality
    according to your specific requirements. By employing the adapter pattern, you
    can effortlessly introduce interventions at the desired points to deviate from
    the standard behavior. This level of customization empowers you to tailor the
    software to meet your unique needs and preferences.

**⚙️ Configuration**
    The required consumer keys and secrets for interacting with Facebook,
    Twitter and the likes can be configured using regular settings, or, can be
    configured in the database via the Django admin. Here, optional support for
    the Django sites framework is available, which is helpful for larger
    multi-domain projects, but also allows for easy switching between a
    development (localhost) and production setup without messing with your
    settings and database.


.. end-features


Commercial Support
==================

.. begin-support

Commercial support is available. If you find certain functionality missing, or
require assistance on your project(s), please contact us: info@intenct.nl.

.. end-support


Cross-Selling
=============

If you like this, you may also like:

- django-trackstats: https://github.com/pennersr/django-trackstats
- netwell: https://github.com/pennersr/netwell
- Shove: https://github.com/pennersr/shove
