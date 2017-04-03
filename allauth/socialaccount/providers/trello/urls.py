from allauth.socialaccount.providers.oauth.urls import default_urlpatterns

from .provider import TrelloProvider


urlpatterns = default_urlpatterns(TrelloProvider)
