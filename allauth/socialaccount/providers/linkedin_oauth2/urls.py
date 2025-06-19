from allauth.socialaccount.providers.linkedin_oauth2.provider import (
    LinkedInOAuth2Provider,
)
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(LinkedInOAuth2Provider)
