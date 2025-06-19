from allauth.socialaccount.providers.exist.provider import ExistProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(ExistProvider)
