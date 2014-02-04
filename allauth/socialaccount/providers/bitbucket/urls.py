from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from .provider import BitbucketProvider

urlpatterns = default_urlpatterns(BitbucketProvider)
