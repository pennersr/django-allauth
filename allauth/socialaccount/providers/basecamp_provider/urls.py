from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import BasecampProvider


urlpatterns = default_urlpatterns(BasecampProvider)
