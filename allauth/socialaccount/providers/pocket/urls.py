from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.pocket.provider import PocketProvider


urlpatterns = default_urlpatterns(PocketProvider)
