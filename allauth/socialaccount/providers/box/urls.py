from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import BoxOAuth2Provider


urlpatterns = default_urlpatterns(BoxOAuth2Provider)
