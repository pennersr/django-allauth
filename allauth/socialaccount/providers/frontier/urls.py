from allauth.socialaccount.providers.frontier.provider import FrontierProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(FrontierProvider)
