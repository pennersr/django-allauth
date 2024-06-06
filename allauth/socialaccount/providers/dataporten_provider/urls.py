from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import DataportenProvider


urlpatterns = default_urlpatterns(DataportenProvider)
