from allauth.socialaccount.providers.agave.views import AgaveAdapter
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AgaveAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("web_url", "dflt")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url", "dflt")


class AgaveProvider(OAuth2Provider):
    id = "agave"
    name = "Agave"
    account_class = AgaveAccount
    oauth2_adapter_class = AgaveAdapter

    def extract_uid(self, data):
        return str(data.get("create_time"))

    def extract_common_fields(self, data):
        return dict(
            email=data.get("email"),
            username=data.get("username", ""),
            name=(f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()),
        )

    def get_default_scope(self):
        scope = ["PRODUCTION"]
        return scope


provider_classes = [AgaveProvider]
