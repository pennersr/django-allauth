from django.conf import settings

TWITTER_ENABLED = 'allauth.twitter' in settings.INSTALLED_APPS
OPENID_ENABLED = 'allauth.openid' in settings.INSTALLED_APPS
SOCIALACCOUNT_ENABLED = 'allauth.socialaccount' in settings.INSTALLED_APPS
FACEBOOK_ENABLED = 'allauth.facebook' in settings.INSTALLED_APPS

assert (not TWITTER_ENABLED and not OPENID_ENABLED and not FACEBOOK_ENABLED) or SOCIALACCOUNT_ENABLED

