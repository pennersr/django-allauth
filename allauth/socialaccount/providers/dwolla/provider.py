"""Provider for Dwolla"""

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DwollaAccount(ProviderAccount):
    """Dwolla Account"""
    pass


class DwollaProvider(OAuth2Provider):
    """Provider for Dwolla"""

    id = 'dwolla'
    name = 'Dwolla'
    account_class = DwollaAccount

    def extract_uid(self, data):
        return str(data.get('id', None))

    def extract_common_fields(self, data):
        return dict(
            name=data.get('name'),
        )


provider_classes = [DwollaProvider]
