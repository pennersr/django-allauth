from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import TikTokProvider


urlpatterns = default_urlpatterns(TikTokProvider)
