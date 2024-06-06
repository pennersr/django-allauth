from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import PinterestProvider


urlpatterns = default_urlpatterns(PinterestProvider)
