from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import PaypalProvider


urlpatterns = default_urlpatterns(PaypalProvider)
