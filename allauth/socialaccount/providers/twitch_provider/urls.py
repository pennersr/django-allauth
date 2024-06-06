from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import TwitchProvider


urlpatterns = default_urlpatterns(TwitchProvider)
