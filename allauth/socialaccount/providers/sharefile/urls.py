from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from allauth.socialaccount.providers.sharefile.provider import ShareFileProvider


urlpatterns = default_urlpatterns(ShareFileProvider)
