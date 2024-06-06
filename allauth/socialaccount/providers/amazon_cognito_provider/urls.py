from allauth.socialaccount.providers.amazon_cognito_provider.provider import (
    AmazonCognitoProvider,
)
from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AmazonCognitoProvider)
