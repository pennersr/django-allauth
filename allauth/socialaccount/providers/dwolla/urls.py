from allauth.socialaccount.providers.dwolla.provider import DwollaProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DwollaProvider)
