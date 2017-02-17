from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import NaverProvider


urlpatterns = default_urlpatterns(NaverProvider)
