from allauth.account.models import EmailAddress
from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FigmaAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('handle', '')

    def get_avatar_url(self):
        return self.account.extra_data.get('img_url', '')


class FigmaProvider(OAuth2Provider):
    id = 'figma'
    name = 'Figma'
    account_class = FigmaAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return {
            'email': data.get('email'),
            'name': data.get('handle'),
        }

    def extract_email_addresses(self, data):
        email = EmailAddress(
            email=data.get('email'),
            primary=True,
            verified=False,
        )
        return [email]


providers.registry.register(FigmaProvider)
