from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import BasecampProvider

urlpatterns = default_urlpatterns(BasecampProvider)
