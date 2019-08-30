from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import OpenStreetMapProvider


urlpatterns = default_urlpatterns(OpenStreetMapProvider)
