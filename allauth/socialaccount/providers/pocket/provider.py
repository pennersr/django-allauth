from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class PocketAccount(ProviderAccount):
    def to_str(self):
        dflt = super(PocketAccount, self).to_str()
        return self.account.extra_data.get("Display_Name", dflt)


class PocketProvider(OAuthProvider):
    id = "pocket"
    name = "Pocket"
    account_class = PocketAccount

    def extract_uid(self, data):
        return data["username"]

    def extract_common_fields(self, data):
        return dict(
            email=data["username"],
        )

    def extract_email_addresses(self, data):
        return [
            EmailAddress(
                email=data["username"],
                verified=True,
                primary=True,
            )
        ]


provider_classes = [PocketProvider]
