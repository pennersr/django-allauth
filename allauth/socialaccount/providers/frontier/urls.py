from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import FrontierProvider


urlpatterns = default_urlpatterns(FrontierProvider)
