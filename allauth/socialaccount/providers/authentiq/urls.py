from allauth.socialaccount.providers.authentiq.provider import AuthentiqProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AuthentiqProvider)
