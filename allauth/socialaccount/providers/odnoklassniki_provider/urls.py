from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import OdnoklassnikiProvider


urlpatterns = default_urlpatterns(OdnoklassnikiProvider)
