from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from openid.consumer.discover import DiscoveryFailure

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import render_authentication_error
from allauth.socialaccount.providers.openid.provider import (
    OpenIDAccount,
    OpenIDProvider,
)
from allauth.socialaccount.providers.openid.views import _openid_consumer


if "allauth.socialaccount.providers.openid" not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured(
        "The steam provider requires 'allauth.socialaccount.providers.openid' to be installed"
    )


STEAM_OPENID_URL = "https://steamcommunity.com/openid"


class SteamAccount(OpenIDAccount):
    def to_str(self):
        dflt = super(SteamAccount, self).to_str()
        return self.account.extra_data.get("personaname", dflt)

    def get_profile_url(self):
        return self.account.extra_data.get("profileurl")

    def get_avatar_url(self):
        return (
            self.account.extra_data.get("avatarfull")
            or self.account.extra_data.get("avatarmedium")
            or self.account.extra_data.get("avatar")
        )


def extract_steam_id(url):
    prefix = "https://steamcommunity.com/openid/id/"
    if not url.startswith(prefix):
        raise ValueError(url)
    return url[len(prefix) :]


def request_steam_account_summary(api_key, steam_id):
    api_base = "https://api.steampowered.com/"
    method = "ISteamUser/GetPlayerSummaries/v0002/"
    params = {"key": api_key, "steamids": steam_id}

    with get_adapter().get_requests_session() as sess:
        resp = sess.get(api_base + method, params=params)
        resp.raise_for_status()
        data = resp.json()

    playerlist = data.get("response", {}).get("players", [])
    return playerlist[0] if playerlist else {"steamid": steam_id}


class SteamOpenIDProvider(OpenIDProvider):
    id = "steam"
    name = "Steam"
    account_class = SteamAccount
    uses_apps = True
    supports_redirect = True

    def __init__(self, request, app=None):
        if app is None:
            app = get_adapter().get_app(request, self.id)
        super().__init__(request, app=app)

    def get_login_url(self, request, **kwargs):
        url = reverse("steam_login")
        if kwargs:
            url += f"?{urlencode(kwargs)}"
        return url

    def sociallogin_from_response(self, request, response):
        steam_id = extract_steam_id(response.identity_url)
        steam_api_key = self.app.secret
        response._extra = request_steam_account_summary(steam_api_key, steam_id)
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

    def get_realm(self, request):
        return self.get_settings().get("REALM", request.build_absolute_uri("/"))

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        endpoint = STEAM_OPENID_URL
        realm = self.get_realm(request)
        try:
            client = _openid_consumer(request, self, endpoint)
            auth_request = client.begin(endpoint)
        except (UnicodeDecodeError, DiscoveryFailure) as e:
            return render_authentication_error(request, self, exception=e)

        self.stash_redirect_state(request, process, next_url, data, **kwargs)

        redirect_url = auth_request.redirectURL(
            realm, request.build_absolute_uri(reverse("steam_callback"))
        )
        return HttpResponseRedirect(redirect_url)


provider_classes = [SteamOpenIDProvider]
