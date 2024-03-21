from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import KlaviyoProvider


urlpatterns = default_urlpatterns(KlaviyoProvider)
