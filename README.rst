==============
Django AllAuth
==============

Integrated set of Django applications addressing authentication,
registration, account management as well as 3rd party (social) account
authentication.

Installation
============

Django
------

settings.py:

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        "allauth.account.context_processors.account"
    )
    
    INSTALLED_APPS = (
        ...
        'emailconfirmation',
	'uni_form',

        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.twitter',
        'allauth.openid',
        'allauth.facebook',

urls.py:

    urlpatterns = patterns('',
        ...
        (r'^accounts/', include('allauth.urls')))


Configuration
=============

Available settings:

ACCOUNT_EMAIL_REQUIRED (=False)
  The user is required to hand over an e-mail address when signing up

ACCOUNT_EMAIL_VERIFICATION (=False)
  After signing up, keep the user account inactive until the e-mail
  address is verified

ACCOUNT_EMAIL_AUTHENTICATION (=False)
  Login by e-mail address, not username

ACCOUNT_UNIQUE_EMAIL (=True)
  Enforce uniqueness of e-mail addresses

SOCIALACCOUNT_QUERY_EMAIL (=ACCOUNT_EMAIL_REQUIRED)
  Request e-mail address from 3rd party account provider? E.g. using
  OpenID AX, or the Facebook "email" permission

SOCIALACCOUNT_AUTO_SIGNUP (=True) 
  Attempt to bypass the signup form by using fields (e.g. username,
  email) retrieved from the social account provider. If a conflict
  arises due to a duplicate e-mail address the signup form will still
  kick in.


Facebook & Twitter
------------------

The required keys and secrets for interacting with Facebook and
Twitter are to be configured in the database via the Django admin
using the TwitterApp and FacebookApp models. 
