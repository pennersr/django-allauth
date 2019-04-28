from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import StripeExpressProvider


urlpatterns = default_urlpatterns(StripeExpressProvider)
