from allauth.socialaccount.providers.agave_provider.provider import AgaveProvider
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AgaveProvider)
