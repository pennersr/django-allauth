# -*- coding: utf-8 -*-
import functools

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class OpenIDConnectProviderAccount(ProviderAccount):
    def to_str(self):
        dflt = super(OpenIDConnectProviderAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class OpenIDConnectProvider(OAuth2Provider):
    id = "openid-connect"
    name = "OpenID Connect"
    _server_id = None
    _server_url = None
    account_class = OpenIDConnectProviderAccount

    @functools.cached_property
    def server_url(self):
        well_known_uri = "/.well-known/openid-configuration"
        url = self._server_url
        if not url.endswith(well_known_uri):
            url += well_known_uri
        return url

    @classmethod
    def get_slug(cls):
        return f"oidc/{cls._server_id}"

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("preferred_username"),
            name=data.get("name"),
            user_id=data.get("user_id"),
            picture=data.get("picture"),
        )


def _provider_factory(server_settings):
    class OpenIDConnectProviderServer(OpenIDConnectProvider):
        name = server_settings.get("name", OpenIDConnectProvider.name)
        id = f"{OpenIDConnectProvider.id}_{server_settings['id']}"
        _server_id = server_settings["id"]
        _server_url = server_settings["openid_url"]

    return OpenIDConnectProviderServer


provider_classes = [
    _provider_factory(server_settings)
    for server_settings in app_settings.PROVIDERS.get(
        OpenIDConnectProvider.id, {}
    ).get("SERVERS", [])
]
