from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.zoho.provider import ZohoProvider


urlpatterns = default_urlpatterns(ZohoProvider)
