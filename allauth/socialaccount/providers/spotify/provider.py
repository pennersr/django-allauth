from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class SpotifyAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("external_urls").get("spotify")

    def get_avatar_url(self):
        try:
            return self.account.extra_data.get("images")[0].get("url")
        except IndexError:
            return None

    def to_str(self):
        dflt = super(SpotifyAccount, self).to_str()
        return self.account.extra_data.get("display_name", dflt)


class SpotifyOAuth2Provider(OAuth2Provider):
    id = "spotify"
    name = "Spotify"
    account_class = SpotifyAccount

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(name=data.get("display_name"), email=data.get("email"))

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append("user-read-email")
        return scope


provider_classes = [SpotifyOAuth2Provider]
