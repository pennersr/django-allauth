from allauth.socialaccount.providers.drip.provider import DripProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DripProvider)
