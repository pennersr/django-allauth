from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.xero.views import (
    XeroOAuth2Adapter,
)


class XeroAccount(ProviderAccount):
    def to_str(self):
        fallback = super(XeroAccount, self).to_str()

        # If the extra_data is malformed, exit early
        if not isinstance(self.account.extra_data, dict):
            return fallback

        display_name = self.account.extra_data.get("name")
        # It's very unlikely but still possible that the display_name is None
        # so we'll return or'd against the fallback just incase. We don't want
        # to return None as users of the library expect this to be str.
        return display_name or fallback

    def get_avatar_url(self):
        return None


class XeroProvider(OAuth2Provider):
    id = "xero"
    name = "Xero"
    account_class = XeroAccount
    oauth2_adapter_class = XeroOAuth2Adapter

    def extract_uid(self, data):
        return str(data["xero_userid"])

    def extract_common_fields(self, data):
        return dict(
            email_address=data.get("email"),
            username=data.get("preferred_username"),
            name=data.get("name"),
        )

    def get_default_scope(self):
        return ["openid", "email", "profile"]

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email is not None:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [XeroProvider]
