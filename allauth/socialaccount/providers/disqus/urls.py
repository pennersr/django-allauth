from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import DisqusProvider


urlpatterns = default_urlpatterns(DisqusProvider)
