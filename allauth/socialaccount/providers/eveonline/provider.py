from allauth.socialaccount.app_settings import STORE_TOKENS
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.eveonline.views import (
    EveOnlineOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EveOnlineAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://gate.eveonline.com/Profile/{char_name}".format(
            char_name=self.account.extra_data.get("CharacterName")
        )

    def get_avatar_url(self):
        return ("https://image.eveonline.com/Character/{char_id}_128.jpg").format(
            char_id=self.account.extra_data.get("CharacterID", 1)
        )

    def to_str(self):
        dflt = super(EveOnlineAccount, self).to_str()
        return next(
            value
            for value in (
                self.account.extra_data.get("CharacterName", None),
                self.account.extra_data.get("CharacterID", None),
                dflt,
            )
            if value is not None
        )


class EveOnlineProvider(OAuth2Provider):
    id = "eveonline"
    name = "EVE Online"
    account_class = EveOnlineAccount
    oauth2_adapter_class = EveOnlineOAuth2Adapter

    def get_default_scope(self):
        scopes = []
        if STORE_TOKENS:
            scopes.append("publicData")
        return scopes

    def extract_uid(self, data):
        return str(data["CharacterOwnerHash"])

    def extract_common_fields(self, data):
        return dict(name=data.get("CharacterName"))


provider_classes = [EveOnlineProvider]
