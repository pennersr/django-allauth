from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class StripeExpressAccount(ProviderAccount):
    def to_str(self):
        default = super(StripeExpressAccount, self).to_str()
        return self.account.extra_data.get('business_name', default)


class StripeExpressProvider(OAuth2Provider):
    id = 'stripe_express'
    name = 'Stripe Connect Express'
    account_class = StripeExpressAccount

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(name=data.get('display_name'),
                    email=data.get('email'))

    def get_default_scope(self):
        return ['read_only']


provider_classes = [StripeExpressProvider]
