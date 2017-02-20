from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import LinkedInOAuth2Provider


urlpatterns = default_urlpatterns(LinkedInOAuth2Provider)
