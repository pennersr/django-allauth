from allauth.socialaccount.providers.amazon.provider import AmazonProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AmazonProvider)
