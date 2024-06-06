from allauth.socialaccount.providers.oauth2_provider.urls import default_urlpatterns

from .provider import BattleNetProvider


urlpatterns = default_urlpatterns(BattleNetProvider)
