from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import MeetupProvider


urlpatterns = default_urlpatterns(MeetupProvider)
