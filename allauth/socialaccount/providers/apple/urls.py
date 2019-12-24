from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AppleProvider


urlpatterns = default_urlpatterns(AppleProvider)
