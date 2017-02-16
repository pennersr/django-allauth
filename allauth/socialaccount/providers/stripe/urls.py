from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import StripeProvider


urlpatterns = default_urlpatterns(StripeProvider)
