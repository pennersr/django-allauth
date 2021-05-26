from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AngelListAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("angellist_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("image")

    def to_str(self):
        dflt = super(AngelListAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class AngelListProvider(OAuth2Provider):
    id = "angellist"
    name = "AngelList"
    account_class = AngelListAccount

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("angellist_url").split("/")[-1],
            name=data.get("name"),
        )


provider_classes = [AngelListProvider]
