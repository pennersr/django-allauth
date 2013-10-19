from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AngelAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('angellist_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('image')

    def to_str(self):
        dflt = super(AngelAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class AngelProvider(OAuth2Provider):
    id = 'angel'
    name = 'Angel List'
    package = 'allauth.socialaccount.providers.angel'
    account_class = AngelAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        print data
        return dict(email=data.get('email'),
                    username=data.get('angellist_url').split('/')[-1],
                    first_name=data.get('name').split(' ')[0],
                    last_name=data.get('name').split(' ')[-1]
                    )


providers.registry.register(AngelProvider)
