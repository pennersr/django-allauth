"""Register urls for EventbriteProvider"""

from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import EventbriteProvider


urlpatterns = default_urlpatterns(EventbriteProvider)
