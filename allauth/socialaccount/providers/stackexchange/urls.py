from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.stackexchange.provider import StackExchangeProvider


urlpatterns = default_urlpatterns(StackExchangeProvider)
