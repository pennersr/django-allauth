from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class PingIdentityAccount(ProviderAccount):
    pass


class PingIdentityProvider(OAuth2Provider):
    id = "pingidentity"
    name = "Ping Identity"
    account_class = PingIdentityAccount

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        return str(data["preferred_username"])

    def extract_extra_data(self, data):
        return data

    def extract_email_addresses(self, data):
        # Assume emails are verified as there is no such claim, but this is a corporate (not end-user) provider.
        return [EmailAddress(email=data["email"], verified=True, primary=True)]

    def extract_common_fields(self, data):
        email = data["email"]

        # Try the attributes seen in testing first, then the ones as per the docs.
        last_name = data.get("lastName") or data.get("family_name") or ""
        first_name = data.get("firstName") or data.get("given_name") or ""

        return dict(email=email, last_name=last_name, first_name=first_name)


provider_classes = [PingIdentityProvider]
