from allauth.socialaccount.providers.agave.provider import AgaveProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AgaveProvider)
