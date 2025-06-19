from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.paypal.provider import PaypalProvider


urlpatterns = default_urlpatterns(PaypalProvider)
