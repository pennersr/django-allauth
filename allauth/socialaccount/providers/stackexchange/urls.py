from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import StackExchangeProvider

urlpatterns = default_urlpatterns(StackExchangeProvider)

