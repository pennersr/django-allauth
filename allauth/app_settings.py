from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib


if 'allauth.twitter' in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("settings.INSTALLED_APPS: use allauth.socialaccount.providers.twitter instead of allauth.twitter")

TWITTER_ENABLED = 'allauth.socialaccount.providers.twitter' in settings.INSTALLED_APPS
OPENID_ENABLED = 'allauth.openid' in settings.INSTALLED_APPS
SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS
FACEBOOK_ENABLED = 'allauth.facebook' in settings.INSTALLED_APPS

assert (not TWITTER_ENABLED and not OPENID_ENABLED and not FACEBOOK_ENABLED) or SOCIALACCOUNT_ENABLED
