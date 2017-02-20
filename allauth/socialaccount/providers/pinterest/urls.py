from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import PinterestProvider


urlpatterns = default_urlpatterns(PinterestProvider)
