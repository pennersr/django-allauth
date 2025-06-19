from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.tiktok.provider import TikTokProvider


urlpatterns = default_urlpatterns(TikTokProvider)
