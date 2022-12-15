# -*- coding: utf-8 -*-
from allauth.account.models import EmailAddress
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class OpenIDConnectProviderAccount(ProviderAccount):
    def to_str(self):
        dflt = super(OpenIDConnectProviderAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class OpenIDConnectProvider(OAuth2Provider):
    id = "openid_connect"
    name = "OpenID Connect"
    _server_id = None
    _server_url = None
    account_class = OpenIDConnectProviderAccount

    @property
    def server_url(self):
        well_known_uri = "/.well-known/openid-configuration"
        url = self._server_url
        if not url.endswith(well_known_uri):
            url += well_known_uri
        return url

    @property
    def token_auth_method(self):
        return app_settings.PROVIDERS.get(self.id, {}).get("token_auth_method")

    @classmethod
    def get_slug(cls):
        return cls._server_id if cls._server_id else "openid_connect"

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_common_fields(self, data):
        return dict(
            username=data.get("preferred_username"),
            name=data.get("name"),
            user_id=data.get("user_id"),
            picture=data.get("picture"),
        )

    def extract_email_addresses(self, data):
        addresses = []
        email = data.get("email")
        if email:
            addresses.append(
                EmailAddress(
                    email=email,
                    verified=data.get("email_verified", False),
                    primary=True,
                )
            )
        return addresses


def _provider_factory(server_settings):
    class OpenIDConnectProviderServer(OpenIDConnectProvider):
        name = server_settings.get("name", OpenIDConnectProvider.name)
        id = server_settings["id"]
        _server_id = server_settings["id"]
        _server_url = server_settings["server_url"]

        def get_app(self, request, config=None):
            return super().get_app(request, config=server_settings.get("APP"))

    OpenIDConnectProviderServer.__name__ = (
        "OpenIDConnectProviderServer_" + server_settings["id"]
    )
    app_settings.PROVIDERS.setdefault(OpenIDConnectProviderServer.id, {})
    app_settings.PROVIDERS[OpenIDConnectProviderServer.id].update(server_settings)
    return OpenIDConnectProviderServer


provider_classes = [
    _provider_factory(server_settings)
    for server_settings in app_settings.PROVIDERS.get(OpenIDConnectProvider.id, {}).get(
        "SERVERS", []
    )
]
