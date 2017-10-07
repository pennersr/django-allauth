from allauth.socialaccount import app_settings
from allauth.account.models import EmailAddress
from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import (ProviderAccount, AuthAction)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class SalesforceAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super(SalesforceAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class SalesforceProvider(OAuth2Provider):
    id = 'salesforce'
    name = 'Salesforce'
    package = 'allauth.socialaccount.providers.salesforce'
    account_class = SalesforceAccount

    def get_default_scope(self):
        return ['id', 'openid']

    def get_auth_params(self, request, action):
        ret = super(SalesforceProvider, self).get_auth_params(request, action)
        if action == AuthAction.REAUTHENTICATE:
            ret['approval_prompt'] = 'force'
        return ret

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('family_name'),
                    first_name=data.get('given_name'))

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email and data.get('verified_email'):
            ret.append(EmailAddress(email=email,
                                    verified=True,
                                    primary=True))
        return ret


providers.registry.register(SalesforceProvider)
