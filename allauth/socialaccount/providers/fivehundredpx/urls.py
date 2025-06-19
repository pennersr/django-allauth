from allauth.socialaccount.providers.fivehundredpx.provider import FiveHundredPxProvider
from allauth.socialaccount.providers.oauth.urls import default_urlpatterns


urlpatterns = default_urlpatterns(FiveHundredPxProvider)
