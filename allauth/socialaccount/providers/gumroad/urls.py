from allauth.socialaccount.providers.gumroad.provider import GumroadProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GumroadProvider)
