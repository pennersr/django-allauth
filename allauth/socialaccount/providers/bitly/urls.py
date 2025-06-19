from allauth.socialaccount.providers.bitly.provider import BitlyProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(BitlyProvider)
