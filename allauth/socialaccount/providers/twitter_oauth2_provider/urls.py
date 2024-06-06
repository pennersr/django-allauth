from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import TwitterOAuth2Provider


urlpatterns = default_urlpatterns(TwitterOAuth2Provider)
