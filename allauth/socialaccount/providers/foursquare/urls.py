from allauth.socialaccount.providers.foursquare.provider import FoursquareProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(FoursquareProvider)
