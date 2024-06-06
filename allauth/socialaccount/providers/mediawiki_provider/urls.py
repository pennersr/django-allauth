from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import MediaWikiProvider


urlpatterns = default_urlpatterns(MediaWikiProvider)
