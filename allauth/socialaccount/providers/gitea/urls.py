from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import GiteaProvider


urlpatterns = default_urlpatterns(GiteaProvider)
