from allauth.socialaccount.providers.edx.provider import EdxProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(EdxProvider)
