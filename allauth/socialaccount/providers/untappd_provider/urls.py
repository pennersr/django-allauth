from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import UntappdProvider


urlpatterns = default_urlpatterns(UntappdProvider)
