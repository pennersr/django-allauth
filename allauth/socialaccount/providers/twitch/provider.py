from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class TwitchAccount(ProviderAccount):
    def get_profile_url(self):
        return "http://twitch.tv/" + self.account.extra_data.get("login")

    def get_avatar_url(self):
        # We're using `logo` as a failback for legacy profiles retrieved
        # with the old https://api.twitch.tv/kraken/user endpoint.
        logo = self.account.extra_data.get("logo")
        return self.account.extra_data.get("profile_image_url", logo)

    def to_str(self):
        dflt = super(TwitchAccount, self).to_str()
        return self.account.extra_data.get("login", dflt)


class TwitchProvider(OAuth2Provider):
    id = "twitch"
    name = "Twitch"
    account_class = TwitchAccount

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return {
            "username": data.get("login"),
            "name": data.get("display_name"),
            "email": data.get("email"),
        }

    def get_default_scope(self):
        return ["user:read:email"]


provider_classes = [TwitchProvider]
