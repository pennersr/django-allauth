from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import FrontierProvider


urlpatterns = default_urlpatterns(FrontierProvider)
