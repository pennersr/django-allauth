from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import TwitchProvider

urlpatterns = default_urlpatterns(TwitchProvider)
