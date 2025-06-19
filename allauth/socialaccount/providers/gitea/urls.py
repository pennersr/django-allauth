from allauth.socialaccount.providers.gitea.provider import GiteaProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(GiteaProvider)
