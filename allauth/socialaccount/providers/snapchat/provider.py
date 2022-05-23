from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    EXTERNAL_ID = "https://auth.snapchat.com/oauth2/api/user.external_id"
    DISPLAY_NAME = "https://auth.snapchat.com/oauth2/api/user.display_name"
    BITMOJI = "https://auth.snapchat.com/oauth2/api/user.bitmoji.avatar"


class SnapchatAccount(ProviderAccount):
    def to_str(self):
        dflt = super(SnapchatAccount, self).to_str()
        return "%s (%s)" % (
            self.account.extra_data.get("data").get("me").get("displayName", ""),
            dflt,
        )


class SnapchatProvider(OAuth2Provider):
    id = "snapchat"
    name = "Snapchat"
    account_class = SnapchatAccount

    def get_default_scope(self):
        scope = [Scope.EXTERNAL_ID, Scope.DISPLAY_NAME]
        return scope

    def extract_uid(self, data):
        return str(data.get("data").get("me").get("externalId"))

    def extract_common_fields(self, data):
        user = data.get("data", {}).get("me")
        return {"name": user.get("displayName")}


provider_classes = [SnapchatProvider]
