from allauth.socialaccount.providers.atlassian.provider import AtlassianProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AtlassianProvider)
