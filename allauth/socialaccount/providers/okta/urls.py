from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import OktaProvider


urlpatterns = default_urlpatterns(OktaProvider)
