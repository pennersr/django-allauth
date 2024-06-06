from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import MeetupProvider


urlpatterns = default_urlpatterns(MeetupProvider)
