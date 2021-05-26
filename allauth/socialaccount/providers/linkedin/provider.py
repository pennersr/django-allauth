from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class LinkedInAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("public-profile-url")

    def get_avatar_url(self):
        # try to return the higher res picture-urls::(original) first
        try:
            if self.account.extra_data.get("picture-urls", {}).get("picture-url"):
                return self.account.extra_data.get("picture-urls", {}).get(
                    "picture-url"
                )
        except Exception:
            # if we can't get higher res for any reason, we'll just return the
            # low res
            pass
        return self.account.extra_data.get("picture-url")

    def to_str(self):
        dflt = super(LinkedInAccount, self).to_str()
        name = self.account.extra_data.get("name", dflt)
        first_name = self.account.extra_data.get("first-name", None)
        last_name = self.account.extra_data.get("last-name", None)
        if first_name and last_name:
            name = first_name + " " + last_name
        return name


class LinkedInProvider(OAuthProvider):
    id = "linkedin"
    name = "LinkedIn"
    account_class = LinkedInAccount

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append("r_emailaddress")
        return scope

    def get_profile_fields(self):
        default_fields = [
            "id",
            "first-name",
            "last-name",
            "email-address",
            "picture-url",
            "picture-urls::(original)",
            # picture-urls::(original) is higher res
            "public-profile-url",
        ]
        fields = self.get_settings().get("PROFILE_FIELDS", default_fields)
        return fields

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email-address"),
            first_name=data.get("first-name"),
            last_name=data.get("last-name"),
        )


provider_classes = [LinkedInProvider]
