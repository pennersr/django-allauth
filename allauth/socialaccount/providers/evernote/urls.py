from allauth.socialaccount.providers.evernote.provider import EvernoteProvider
from allauth.socialaccount.providers.oauth.urls import default_urlpatterns


urlpatterns = default_urlpatterns(EvernoteProvider)
