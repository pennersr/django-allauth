from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.miro.views import MiroOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MiroAccount(ProviderAccount):
    pass


class MiroProvider(OAuth2Provider):
    id = "miro"
    name = "Miro"
    account_class = MiroAccount
    oauth2_adapter_class = MiroOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(email=data.get("email"), name=data.get("name"))

    def get_default_scope(self):
        return ["identity:read"]

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email and data.get("state") == "registered":
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [MiroProvider]
