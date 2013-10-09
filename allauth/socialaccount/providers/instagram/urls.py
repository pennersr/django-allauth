from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import InstagramProvider

urlpatterns = default_urlpatterns(InstagramProvider)

