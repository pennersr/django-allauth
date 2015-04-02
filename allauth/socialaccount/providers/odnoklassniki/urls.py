from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import OdnoklassnikiProvider

urlpatterns = default_urlpatterns(OdnoklassnikiProvider)
