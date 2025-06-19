from allauth.socialaccount.providers.naver.provider import NaverProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(NaverProvider)
