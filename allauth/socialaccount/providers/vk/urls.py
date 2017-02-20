from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import VKProvider


urlpatterns = default_urlpatterns(VKProvider)
