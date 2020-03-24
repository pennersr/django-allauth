from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AppleProvider(OAuth2Provider):
    id = 'apple'
    name = 'Apple'
    account_class = ProviderAccount

    def extract_uid(self, data):
        return str(data['sub'])

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email and data.get('email_verified'):
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [AppleProvider]
