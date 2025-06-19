from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.orcid.provider import OrcidProvider


urlpatterns = default_urlpatterns(OrcidProvider)
