from allauth.socialaccount.providers.daum.provider import DaumProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(DaumProvider)
