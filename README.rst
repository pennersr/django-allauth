==============
Django AllAuth
==============

Integrated set of Django applications addressing authentication,
registration, account management as well as 3rd party (social) account
authentication.

Configuration
=============

Django
------

settings.py:

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        "allauth.account.context_processors.account"
    )
    
    INSTALLED_APPS = (
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


Facebook & Twitter
------------------

The required keys and secrets for interacting with Facebook and
Twitter are to be configured in the database via the Django admin
using the TwitterApp and FacebookApp models. 
