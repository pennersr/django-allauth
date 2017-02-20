from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class PaypalAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        return self.account.extra_data.get('name',
                                           super(PaypalAccount, self).to_str())


class PaypalProvider(OAuth2Provider):
    id = 'paypal'
    name = 'Paypal'
    account_class = PaypalAccount

    def get_default_scope(self):
        # See: https://developer.paypal.com/docs/integration/direct/identity/attributes/  # noqa
        return ['openid', 'email']

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        # See: https://developer.paypal.com/docs/api/#get-user-information
        return dict(first_name=data.get('given_name', ''),
                    last_name=data.get('family_name', ''),
                    email=data.get('email'))


providers.registry.register(PaypalProvider)
