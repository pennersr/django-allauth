from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import KakaoProvider


urlpatterns = default_urlpatterns(KakaoProvider)
