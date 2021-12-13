from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BitlyAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("profile_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("profile_image")

    def to_str(self):
        dflt = super(BitlyAccount, self).to_str()
        return "%s (%s)" % (
            self.account.extra_data.get("full_name", ""),
            dflt,
        )


class BitlyProvider(OAuth2Provider):
    id = "bitly"
    name = "Bitly"
    account_class = BitlyAccount

    def extract_uid(self, data):
        return str(data["login"])

    def extract_common_fields(self, data):
        return dict(username=data["login"], name=data.get("full_name"))


provider_classes = [BitlyProvider]
