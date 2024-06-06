from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import OktaProvider


urlpatterns = default_urlpatterns(OktaProvider)
