from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import FeedlyProvider


urlpatterns = default_urlpatterns(FeedlyProvider)
