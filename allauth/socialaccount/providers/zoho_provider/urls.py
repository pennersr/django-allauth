from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import ZohoProvider


urlpatterns = default_urlpatterns(ZohoProvider)
