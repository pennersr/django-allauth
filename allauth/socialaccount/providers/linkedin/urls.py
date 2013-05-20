from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from .provider import LinkedInProvider

urlpatterns = default_urlpatterns(LinkedInProvider)
