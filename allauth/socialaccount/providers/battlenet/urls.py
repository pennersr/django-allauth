from allauth.socialaccount.providers.battlenet.provider import BattleNetProvider
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = default_urlpatterns(BattleNetProvider)
