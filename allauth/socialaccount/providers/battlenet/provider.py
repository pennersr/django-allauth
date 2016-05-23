from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class BattleNetSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if "battletag" in data:
            user.username = data["battletag"]
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.username = sociallogin.account.extra_data["battletag"]
        user.save()

        return user


class BattleNetAccount(ProviderAccount):
    pass


class BattleNetProvider(OAuth2Provider):
    id = "battlenet"
    name = "Battle.net"
    account_class = BattleNetAccount

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return {"battletag": data.get("battletag")}

    def get_default_scope(self):
        # Optional scopes: "sc2.profile", "wow.profile"
        return []

providers.registry.register(BattleNetProvider)
