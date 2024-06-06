from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import FoursquareProvider


urlpatterns = default_urlpatterns(FoursquareProvider)
