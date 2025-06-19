from allauth.socialaccount.providers.digitalocean.provider import DigitalOceanProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DigitalOceanProvider)
