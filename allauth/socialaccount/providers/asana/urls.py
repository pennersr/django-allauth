from allauth.socialaccount.providers.asana.provider import AsanaProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AsanaProvider)
