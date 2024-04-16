from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import XeroProvider


urlpatterns = default_urlpatterns(XeroProvider)
