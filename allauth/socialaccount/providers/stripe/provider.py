from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount import app_settings


class StripeAccount(ProviderAccount):
    pass


class StripeProvider(OAuth2Provider):
    id = 'stripe'
    name = 'Stripe'
    account_class = StripeAccount

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(name=data.get('display_name'),
                    email=data.get('email'))

    def get_default_scope(self):
        return ['read_only']

providers.registry.register(StripeProvider)
