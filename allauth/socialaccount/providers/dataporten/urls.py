from allauth.socialaccount.providers.dataporten.provider import DataportenProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DataportenProvider)
