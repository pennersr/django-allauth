from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import SalesforceProvider


urlpatterns = default_urlpatterns(SalesforceProvider)
