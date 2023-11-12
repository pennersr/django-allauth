from django.urls import reverse
from django.utils.http import urlencode

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class OpenIDConnectProviderAccount(ProviderAccount):
    def to_str(self):
        dflt = super(OpenIDConnectProviderAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class OpenIDConnectProvider(OAuth2Provider):
    id = "openid_connect"
    name = "OpenID Connect"
    account_class = OpenIDConnectProviderAccount

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.app.name

    @property
    def server_url(self):
        url = self.app.settings["server_url"]
        return self.wk_server_url(url)

    def wk_server_url(self, url):
        well_known_uri = "/.well-known/openid-configuration"
        if not url.endswith(well_known_uri):
            url += well_known_uri
        return url

    def get_login_url(self, request, **kwargs):
        url = reverse(
            self.app.provider + "_login", kwargs={"provider_id": self.app.provider_id}
        )
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def get_callback_url(self):
        return reverse(
            self.app.provider + "_callback",
            kwargs={"provider_id": self.app.provider_id},
        )

    @property
    def token_auth_method(self):
        return self.app.settings.get("token_auth_method")

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        return str(data["sub"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
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


provider_classes = [OpenIDConnectProvider]
