from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

class AmazonAccount(ProviderAccount):
    def to_str(self):
        name = self.account.extra_data.get('name', '')
        if name != '':
            return name
        return super(AmazonAccount, self).to_str()

class AmazonProvider(OAuth2Provider):
    id = 'amazon'
    name = 'Amazon'
    package = 'allauth.socialaccount.providers.amazon'
    account_class = AmazonAccount

    def get_default_scope(self):
        return ['profile']
    
    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        name = data.get('name', '')
        first_name, last_name = name, ''
        if name and ' ' in name:
            first_name, last_name = name.split(' ', 1)
        return dict(email=data['email'], 
                    last_name=last_name,
                    first_name=first_name)

providers.registry.register(AmazonProvider)
