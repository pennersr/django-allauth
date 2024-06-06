from allauth.socialaccount.providers.oauth_provider.urls import default_urlpatterns

from .provider import BoxOAuth2Provider


urlpatterns = default_urlpatterns(BoxOAuth2Provider)
