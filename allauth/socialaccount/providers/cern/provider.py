from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProvider,
    OpenIDConnectProviderAccount,
)


class CernAccount(OpenIDConnectProviderAccount):
    def to_str(self):
        dflt = super(CernAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class CernProvider(OpenIDConnectProvider):
    """
    Child class for logging into CERN, using OIDC.
    """

    id = "cern"
    name = "Cern"

    # Well-known config for CERN
    _server_url = (
        "https://auth.cern.ch/auth/realms/cern/.well-known/openid-configuration"
    )
    account_class = CernAccount

    def extract_uid(self, data):
        return str(data.get("sub"))

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("preferred_username"),
            first_name=data.get("given_name"),
            last_name=data.get("family_name"),
            name=data.get("name"),
        )


provider_classes = [CernProvider]
