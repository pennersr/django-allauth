from allauth.socialaccount.providers.bitbucket_oauth2.provider import (
    BitbucketOAuth2Provider,
)
from allauth.socialaccount.providers.oauth.urls import default_urlpatterns


urlpatterns = default_urlpatterns(BitbucketOAuth2Provider)
