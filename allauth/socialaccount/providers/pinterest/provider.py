from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class PinterestAccount(ProviderAccount):
    def get_profile_url(self):
        # v5 extra_data not same as v1
        if "profile_image" in self.account.extra_data:
            return self.account.extra_data.get("profile_image")
        return self.account.extra_data.get("url")

    def to_str(self):
        dflt = super(PinterestAccount, self).to_str()
        return self.account.extra_data.get("username", dflt)


class PinterestProvider(OAuth2Provider):
    id = "pinterest"
    name = "Pinterest"
    account_class = PinterestAccount

    @property
    def api_version(self):
        return self.get_settings().get("PINTEREST_VERSION", "v1")

    def get_default_scope(self):
        # See: https://developers.pinterest.com/docs/api/overview/#scopes
        if self.api_version == "v5":
            # See: https://developers.pinterest.com/docs/getting-started/scopes/
            return ["user_accounts:read"]
        return ["read_public"]

    def extract_extra_data(self, data):
        if self.api_version == "v5":
            return data
        return data.get("data", {})

    def extract_uid(self, data):
        if self.api_version == "v5":
            return data["username"]
        return str(data["data"]["id"])

    def extract_common_fields(self, data):
        if self.api_version == "v5":
            return dict(
                username=data["username"]
            )
        return dict(
            first_name=data.get("data", {}).get("first_name"),
            last_name=data.get("data", {}).get("last_name"),
        )


provider_classes = [PinterestProvider]
