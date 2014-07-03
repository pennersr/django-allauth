from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import MSLiveProvider

urlpatterns = default_urlpatterns(MSLiveProvider)
