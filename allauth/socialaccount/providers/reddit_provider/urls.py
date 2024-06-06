from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import RedditProvider


urlpatterns = default_urlpatterns(RedditProvider)
