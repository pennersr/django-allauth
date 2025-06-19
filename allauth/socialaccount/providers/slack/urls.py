from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.slack.provider import SlackProvider


urlpatterns = default_urlpatterns(SlackProvider)
