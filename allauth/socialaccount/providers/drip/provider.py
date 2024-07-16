from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.drip.views import DripOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DripAccount(ProviderAccount):
    pass


class DripProvider(OAuth2Provider):
    id = "drip"
    name = "Drip"
    account_class = DripAccount
    oauth2_adapter_class = DripOAuth2Adapter

    def extract_uid(self, data):
        # no uid available, we generate one by hashing the email
        uid = hash(data.get("email"))
        return str(uid)

    def extract_common_fields(self, data):
        return dict(email=data.get("email"), name=data.get("name"))

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [DripProvider]
