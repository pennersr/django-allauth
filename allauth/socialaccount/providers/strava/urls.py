from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.strava.provider import StravaProvider


urlpatterns = default_urlpatterns(StravaProvider)
