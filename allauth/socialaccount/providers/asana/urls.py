from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AsanaProvider


urlpatterns = default_urlpatterns(AsanaProvider)
