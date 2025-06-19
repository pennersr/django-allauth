from allauth.socialaccount.providers.clever.provider import CleverProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(CleverProvider)
