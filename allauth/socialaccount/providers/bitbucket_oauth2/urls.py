from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import BitbucketOAuth2Provider

urlpatterns = default_urlpatterns(BitbucketOAuth2Provider)
