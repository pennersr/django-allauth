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

from django.urls import reverse

from allauth.socialaccount.providers.openid.views import (
    OpenIDCallbackView,
    OpenIDLoginView,
)
from allauth.socialaccount.providers.steam.provider import SteamOpenIDProvider


STEAM_OPENID_URL = "https://steamcommunity.com/openid"


class SteamOpenIDLoginView(OpenIDLoginView):
    provider_class = SteamOpenIDProvider

    def get_form(self):
        items = dict(list(self.request.GET.items()) + list(self.request.POST.items()))
        items["openid"] = STEAM_OPENID_URL
        return self.form_class(items)

    def get_callback_url(self):
        return reverse(steam_callback)


class SteamOpenIDCallbackView(OpenIDCallbackView):
    provider_class = SteamOpenIDProvider


steam_login = SteamOpenIDLoginView.as_view()
steam_callback = SteamOpenIDCallbackView.as_view()
