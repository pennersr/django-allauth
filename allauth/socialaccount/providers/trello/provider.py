from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class TrelloAccount(ProviderAccount):
    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None


class TrelloProvider(OAuthProvider):
    id = "trello"
    name = "Trello"
    account_class = TrelloAccount

    def get_default_scope(self):
        return ["read"]

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username"),
            name=data.get("name"),
        )

    def get_auth_params(self, request, action):
        data = super(TrelloProvider, self).get_auth_params(request, action)
        data["type"] = "web_server"
        data["name"] = self.app.name
        data["scope"] = self.get_scope(request)
        # define here for how long it will be, this can be configured on the
        # social app
        data["expiration"] = "never"
        return data


provider_classes = [TrelloProvider]
