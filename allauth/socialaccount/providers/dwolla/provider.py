"""Provider for Dwolla"""

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.dwolla.views import DwollaOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DwollaAccount(ProviderAccount):
    pass


class DwollaProvider(OAuth2Provider):
    """Provider for Dwolla"""

    id = "dwolla"
    name = "Dwolla"
    account_class = DwollaAccount
    oauth2_adapter_class = DwollaOAuth2Adapter

    def extract_uid(self, data):
        return str(data.get("id", None))

    def extract_common_fields(self, data):
        return dict(
            name=data.get("name"),
        )


provider_classes = [DwollaProvider]
