from allauth.socialaccount.providers.mediawiki.provider import MediaWikiProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(MediaWikiProvider)
