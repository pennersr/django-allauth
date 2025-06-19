from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.salesforce.provider import SalesforceProvider


urlpatterns = default_urlpatterns(SalesforceProvider)
