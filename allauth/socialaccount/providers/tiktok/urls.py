from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import TikTokProvider


urlpatterns = default_urlpatterns(TikTokProvider)
