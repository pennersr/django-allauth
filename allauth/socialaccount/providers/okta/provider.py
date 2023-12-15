from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class OktaAccount(ProviderAccount):
    def to_str(self):
        dflt = super(OktaAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class OktaProvider(OAuth2Provider):
    id = "okta"
    name = "Okta"
    account_class = OktaAccount

    def get_default_scope(self):
        return ["openid", "profile", "email", "offline_access"]

    def extract_uid(self, data):
        return str(data["preferred_username"])

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
