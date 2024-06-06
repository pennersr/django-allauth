from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import DisqusProvider


urlpatterns = default_urlpatterns(DisqusProvider)
