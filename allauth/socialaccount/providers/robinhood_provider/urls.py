from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import RobinhoodProvider


urlpatterns = default_urlpatterns(RobinhoodProvider)
