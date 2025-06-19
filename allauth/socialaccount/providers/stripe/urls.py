from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.stripe.provider import StripeProvider


urlpatterns = default_urlpatterns(StripeProvider)
