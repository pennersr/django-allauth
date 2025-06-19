from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.twitter_oauth2.provider import (
    TwitterOAuth2Provider,
)


urlpatterns = default_urlpatterns(TwitterOAuth2Provider)
