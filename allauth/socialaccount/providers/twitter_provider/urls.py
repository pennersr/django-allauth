from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import TwitterProvider


urlpatterns = default_urlpatterns(TwitterProvider)
