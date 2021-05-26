from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import ShareFileProvider


urlpatterns = default_urlpatterns(ShareFileProvider)
