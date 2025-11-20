"""
OpenID Adapter for Steam

The Steam login API is simple OpenID but requires extra API calls
for basic resources such as usernames.

Resources:

* Steam Web API Documentation
    https://steamcommunity.com/dev

* Steam Partner API documentation
    https://partner.steamgames.com/doc/features/auth#website
"""

from django.utils.decorators import method_decorator

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.providers.base.views import BaseLoginView
from allauth.socialaccount.providers.openid.views import OpenIDCallbackView
from allauth.socialaccount.providers.steam.provider import SteamOpenIDProvider


@method_decorator(login_not_required, name="dispatch")
class SteamOpenIDLoginView(BaseLoginView):
    provider_id = SteamOpenIDProvider.id


class SteamOpenIDCallbackView(OpenIDCallbackView):
    provider_class = SteamOpenIDProvider


steam_login = SteamOpenIDLoginView.as_view()
steam_callback = SteamOpenIDCallbackView.as_view()
