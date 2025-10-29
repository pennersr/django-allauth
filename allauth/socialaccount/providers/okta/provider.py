from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.okta.views import OktaOAuth2Adapter


class OktaAccount(ProviderAccount):
    pass


class OktaProvider(OAuth2Provider):
    id = "okta"
    name = "Okta"
    account_class = OktaAccount
    oauth2_adapter_class = OktaOAuth2Adapter

    def get_default_scope(self):
        return ["openid", "profile", "email", "offline_access"]

    def extract_uid(self, data):
        uid_field = self.app.settings.get("uid_field", "sub")
        return str(data[uid_field])

    def extract_extra_data(self, data):
        return data

    def extract_email_addresses(self, data):
        return [
            EmailAddress(
                email=data["email"], verified=bool(data["email_verified"]), primary=True
            )
        ]

    def extract_common_fields(self, data):
        ret = dict(
            email=data["email"],
            last_name=data["family_name"],
            first_name=data["given_name"],
        )
        preferred_username = data.get("preferred_username")
        if preferred_username:
            ret["username"] = preferred_username.partition("@")[0]
        return ret


provider_classes = [OktaProvider]
