from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DigitalOceanProvider


urlpatterns = default_urlpatterns(DigitalOceanProvider)
