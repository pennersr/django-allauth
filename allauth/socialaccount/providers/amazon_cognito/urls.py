from allauth.socialaccount.providers.amazon_cognito.provider import (
    AmazonCognitoProvider,
)
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(AmazonCognitoProvider)
