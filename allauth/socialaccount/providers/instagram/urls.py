from allauth.socialaccount.providers.instagram.provider import InstagramProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(InstagramProvider)
