from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import AmazonProvider


urlpatterns = default_urlpatterns(AmazonProvider)
