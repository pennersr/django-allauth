from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import GitHubProvider


urlpatterns = default_urlpatterns(GitHubProvider)
