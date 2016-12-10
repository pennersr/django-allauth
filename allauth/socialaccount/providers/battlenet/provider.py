from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BattleNetAccount(ProviderAccount):
    def to_str(self):
        battletag = self.account.extra_data.get("battletag")
        return battletag or super(BattleNetAccount, self).to_str()


class BattleNetProvider(OAuth2Provider):
    id = "battlenet"
    name = "Battle.net"
    account_class = BattleNetAccount

    def extract_uid(self, data):
        uid = str(data["id"])
        if data.get("region") == "cn":
            # China is on a different account system. UIDs can clash with US.
            return uid + "-cn"
        return uid

    def extract_common_fields(self, data):
        return {"username": data.get("battletag")}

    def get_default_scope(self):
        # Optional scopes: "sc2.profile", "wow.profile"
        return []


providers.registry.register(BattleNetProvider)
