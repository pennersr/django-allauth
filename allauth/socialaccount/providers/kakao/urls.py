from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import KakaoProvider


urlpatterns = default_urlpatterns(KakaoProvider)
