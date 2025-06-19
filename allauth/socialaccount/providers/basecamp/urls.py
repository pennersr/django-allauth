from allauth.socialaccount.providers.basecamp.provider import BasecampProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(BasecampProvider)
