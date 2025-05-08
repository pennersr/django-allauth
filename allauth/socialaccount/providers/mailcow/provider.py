from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.mailcow.views import MailcowAdapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MailcowAccount(ProviderAccount):
    pass


class MailcowProvider(OAuth2Provider):
    id = "mailcow"
    name = "Mailcow"
    account_class = MailcowAccount
    oauth2_adapter_class = MailcowAdapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            username=data["username"],
            name=data["displayName"],
            full_name=data.get("full_name"),
            email=data["email"],
        )

    def get_default_scope(self):
        scope = ["profile"]
        return scope


provider_classes = [MailcowProvider]
