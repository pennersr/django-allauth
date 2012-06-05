from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from models import GitHubProvider

urlpatterns = default_urlpatterns(GitHubProvider)

