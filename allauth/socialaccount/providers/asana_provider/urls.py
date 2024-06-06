from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import AsanaProvider


urlpatterns = default_urlpatterns(AsanaProvider)
