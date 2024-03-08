from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.exist.views import ExistOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class ExistAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://exist.io/api/2/accounts/profile/"

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar")

    def to_str(self):
        name = super().to_str()
        return self.account.extra_data.get("name", name)


class ExistProvider(OAuth2Provider):
    id = "exist"
    name = "Exist.io"
    account_class = ExistAccount
    oauth2_adapter_class = ExistOAuth2Adapter

    def extract_uid(self, data):
        return data.get("username")

    def extract_common_fields(self, data):
        extra_common = super().extract_common_fields(data)
        extra_common.update(
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            avatar=data.get("avatar"),
            timezone=data.get("timezone"),
            local_time=data.get("local_time"),
        )
        return extra_common

    def get_default_scope(self):
        return ["mood_read", "health_read", "productivity_read"]


provider_classes = [ExistProvider]
