Frequently Asked Questions
==========================

Overall
-------

Why don't you implement support for ... ?
*****************************************

This app is just about authentication. Anything that is project
specific, such as making choices on what to display in a profile page,
or, what information is stored for a user (e.g. home address, or
favorite color?), is beyond scope and therefore not offered.

This information is nice and all, but... I need more!
*****************************************************

Here are a few third party resources to help you get started:

- https://speakerdeck.com/tedtieken/signing-up-and-signing-in-users-in-django-with-django-allauth
- http://stackoverflow.com/questions/tagged/django-allauth
- http://www.sarahhagstrom.com/2013/09/the-missing-django-allauth-tutorial/
- https://github.com/aellerton/demo-allauth-bootstrap

I think I found a security issue... now what?
*********************************************

Please report security issues only to django-allauth-security@googlegroups.com.
This is a private list only open to long-time, highly trusted django-allauth
developers, and its archives are not public.

You may also want to subscribe to django-allauth-announce@googlegroups.com to
get notified about security releases.


Troubleshooting
---------------

The /accounts/ URL is giving me a 404
*************************************

There is no such URL. Try `/accounts/login/` instead.

When I attempt to login I run into a 404 on /accounts/profile/
**************************************************************

When you end up here you have successfully logged in. However, you
will need to implement a view for this URL yourself, as whatever is to
be displayed here is project specific. You can also decide to redirect
elsewhere:

https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url

When I sign up I run into connectivity errors (connection refused et al)
************************************************************************

You probably have not got an e-mail (SMTP) server running on the
machine you are developing on. Therefore, `allauth` is unable to send
verification mails.

You can work around this by adding the following line to
``settings.py``:

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

This will avoid the need for an SMTP server as e-mails will be printed
to the console. For more information, please refer to:

https://docs.djangoproject.com/en/dev/ref/settings/#email-host
