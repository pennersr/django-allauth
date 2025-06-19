from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.odnoklassniki.provider import OdnoklassnikiProvider


urlpatterns = default_urlpatterns(OdnoklassnikiProvider)
