from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import PocketProvider


urlpatterns = default_urlpatterns(PocketProvider)
