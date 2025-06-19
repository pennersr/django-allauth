"""Register urls for MailChimpProvider"""

from allauth.socialaccount.providers.mailchimp.provider import MailChimpProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(MailChimpProvider)
