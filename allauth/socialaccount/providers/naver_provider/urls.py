from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import NaverProvider


urlpatterns = default_urlpatterns(NaverProvider)
