from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import SnapchatProvider


urlpatterns = default_urlpatterns(SnapchatProvider)
