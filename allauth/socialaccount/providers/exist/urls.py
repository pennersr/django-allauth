from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import ExistProvider


urlpatterns = default_urlpatterns(ExistProvider)
