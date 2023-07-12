from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class StravaAccount(ProviderAccount):
    def get_profile_url(self):
        id = self.account.extra_data.get("id")
        if id:
            return "https://www.strava.com/athletes/{}".format(id)
        return None

    def get_avatar_url(self):
        avatar = self.account.extra_data.get("profile")
        if avatar and avatar != "avatar/athlete/large.png":
            return avatar
        return None

    def to_str(self):
        name = super(StravaAccount, self).to_str()
        return self.account.extra_data.get("name", name)


class StravaProvider(OAuth2Provider):
    id = "strava"
    name = "Strava"
    account_class = StravaAccount

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
