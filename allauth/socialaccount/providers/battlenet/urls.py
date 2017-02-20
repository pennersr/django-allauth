from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import BattleNetProvider


urlpatterns = default_urlpatterns(BattleNetProvider)
