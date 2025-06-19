from allauth.socialaccount.providers.oauth.urls import default_urlpatterns
from allauth.socialaccount.providers.trello.provider import TrelloProvider


urlpatterns = default_urlpatterns(TrelloProvider)
