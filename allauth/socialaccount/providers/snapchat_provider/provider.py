from allauth.socialaccount.providers.base_provider import ProviderAccount
from allauth.socialaccount.providers.oauth2_provider.provider import OAuth2Provider
from allauth.socialaccount.providers.snapchat_provider.constants import (
    PROVIDER_ID,
    Scope,
)
from allauth.socialaccount.providers.snapchat_provider.views import (
    SnapchatOAuth2Adapter,
)


class SnapchatAccount(ProviderAccount):
    def to_str(self):
        dflt = super(SnapchatAccount, self).to_str()
        return "%s (%s)" % (
            self.account.extra_data.get("data").get("me").get("displayName", ""),
            dflt,
        )


class SnapchatProvider(OAuth2Provider):
    id = PROVIDER_ID
    name = "Snapchat"
    account_class = SnapchatAccount
    oauth2_adapter_class = SnapchatOAuth2Adapter

    def get_default_scope(self):
        scope = [Scope.EXTERNAL_ID, Scope.DISPLAY_NAME]
        return scope

    def extract_uid(self, data):
        return str(data.get("data").get("me").get("externalId"))

    def extract_common_fields(self, data):
        user = data.get("data", {}).get("me")
        return {"name": user.get("displayName")}


provider_classes = [SnapchatProvider]
