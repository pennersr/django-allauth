from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import MicrosoftGraphProvider


urlpatterns = default_urlpatterns(MicrosoftGraphProvider)
