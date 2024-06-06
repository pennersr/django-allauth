"""Register urls for MailChimpProvider"""

from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import MailChimpProvider


urlpatterns = default_urlpatterns(MailChimpProvider)
