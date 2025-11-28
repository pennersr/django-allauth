from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.strava.views import StravaOAuth2Adapter


class StravaAccount(ProviderAccount):
    def get_profile_url(self):
        id = self.account.extra_data.get("id")
        if id:
            return f"https://www.strava.com/athletes/{id}"
        return None

    def get_avatar_url(self):
        avatar = self.account.extra_data.get("profile")
        if avatar and avatar != "avatar/athlete/large.png":
            return avatar
        return None


class StravaProvider(OAuth2Provider):
    id = "strava"
    name = "Strava"
    account_class = StravaAccount
    oauth2_adapter_class = StravaOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        extra_common = super(StravaProvider, self).extract_common_fields(data)
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        name = " ".join(part for part in (firstname, lastname) if part)
        extra_common.update(
            username=data.get("username"),
            email=data.get("email"),
            first_name=firstname,
            last_name=lastname,
            name=name.strip(),
        )
        return extra_common

    def get_default_scope(self):
        return ["read,activity:read"]


provider_classes = [StravaProvider]
