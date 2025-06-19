from allauth.socialaccount.providers.meetup.provider import MeetupProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(MeetupProvider)
