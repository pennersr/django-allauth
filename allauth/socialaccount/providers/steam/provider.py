import requests

from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.openid.provider import (
    OpenIDAccount,
    OpenIDProvider,
)


class SteamAccount(OpenIDAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("profileurl")

    def get_avatar_url(self):
        return (
            self.account.extra_data.get("avatarfull") or
            self.account.extra_data.get("avatarmedium") or
            self.account.extra_data.get("avatar")
        )


def extract_steam_id(url):
    return url.lstrip("https://steamcommunity.com/openid/id/")


def request_steam_account_summary(api_key, steam_id):
    api_base = "https://api.steampowered.com/"
    method = "ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": api_key, "steamids": steam_id}

    resp = requests.get(api_base + method, params)
    data = resp.json()

    playerlist = data.get("response", {}).get("players", [])
    return playerlist[0] if playerlist else {"steamid": steam_id}


class SteamOpenIDProvider(OpenIDProvider):
    id = "steam"
    name = "Steam"
    account_class = SteamAccount

    def get_login_url(self, request, **kwargs):
        url = reverse("steam_login")
        if kwargs:
            url += "?" + urlencode(kwargs)
        return url

    def sociallogin_from_response(self, request, response):
        steam_id = extract_steam_id(response.identity_url)
        steam_api_key = self.get_app(request).secret
        response._extra = request_steam_account_summary(
            steam_api_key, steam_id
        )
        return super(SteamOpenIDProvider, self).sociallogin_from_response(
            request, response
        )

    def extract_uid(self, response):
        return response._extra["steamid"]

    def extract_extra_data(self, response):
        return response._extra.copy()

    def extract_common_fields(self, response):
        full_name = response._extra.get("realname", "").strip()
        if full_name.count(" ") == 1:
            first_name, last_name = full_name.split()
        else:
            first_name, last_name = full_name, ""

        username = response._extra.get("personaname", "")

        return {
            "username": username or response._extra["steamid"],
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
        }


provider_classes = [SteamOpenIDProvider]
