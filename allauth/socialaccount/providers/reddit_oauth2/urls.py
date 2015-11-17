from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from provider import RedditOAuth2Provider

urlpatterns = default_urlpatterns(RedditOAuth2Provider)
