from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import WhaleSpaceProvider


urlpatterns = default_urlpatterns(WhaleSpaceProvider)
