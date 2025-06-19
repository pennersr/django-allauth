from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.twitch.provider import TwitchProvider


urlpatterns = default_urlpatterns(TwitchProvider)
