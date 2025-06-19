from allauth.socialaccount.providers.line.provider import LineProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(LineProvider)
