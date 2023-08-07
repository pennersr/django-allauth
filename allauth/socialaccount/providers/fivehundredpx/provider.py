from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class FiveHundredPxAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://500px.com/%s" % self.account.extra_data.get("username")

    def get_avatar_url(self):
        return self.account.extra_data.get("userpic_url")

    def to_str(self):
        dflt = super(FiveHundredPxAccount, self).to_str()
        name = self.account.extra_data.get("fullname", dflt)
        return name


class FiveHundredPxProvider(OAuthProvider):
    id = "500px"
    name = "500px"
    package = "allauth.socialaccount.providers.fivehundredpx"
    account_class = FiveHundredPxAccount

    def get_default_scope(self):
        return []

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            username=data.get("username"),
            email=data.get("email"),
            first_name=data.get("firstname"),
            last_name=data.get("lastname"),
        )


provider_classes = [FiveHundredPxProvider]
