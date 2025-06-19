from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.okta.provider import OktaProvider


urlpatterns = default_urlpatterns(OktaProvider)
