"""Register urls for EventbriteProvider"""

from allauth.socialaccount.providers.eventbrite.provider import EventbriteProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(EventbriteProvider)
