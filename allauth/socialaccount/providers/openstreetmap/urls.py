from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.openstreetmap.provider import OpenStreetMapProvider


urlpatterns = default_urlpatterns(OpenStreetMapProvider)
