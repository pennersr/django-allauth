from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.hubspot.views import HubspotOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class HubspotAccount(ProviderAccount):
    pass


class HubspotProvider(OAuth2Provider):
    id = "hubspot"
    name = "Hubspot"
    account_class = HubspotAccount
    oauth2_adapter_class = HubspotOAuth2Adapter

    def get_default_scope(self):
        return ["oauth"]

    def extract_uid(self, data):
        return str(data["user_id"])

    def extract_common_fields(self, data):
        return dict(email=data.get("user"))

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("user")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [HubspotProvider]
