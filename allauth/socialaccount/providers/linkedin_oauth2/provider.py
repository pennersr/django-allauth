from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class LinkedInOAuth2Account(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('public-profile-url')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture-url')

    def to_str(self):
        dflt = super(LinkedInOAuth2Account, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        first_name = self.account.extra_data.get('first-name', None)
        last_name = self.account.extra_data.get('last-name', None)
        if first_name and last_name:
            name = first_name+' '+last_name
        return name


class LinkedInOAuth2Provider(OAuth2Provider):
    id = 'linkedin_oauth2'
    name = 'LinkedInOAuth2'
    package = 'allauth.socialaccount.providers.linkedin_oauth2'
    account_class = LinkedInOAuth2Account

    def extract_uid(self, data):
        return str(data['id'])

    def get_profile_fields(self):
        default_fields = ['id',
                          'first-name',
                          'last-name',
                          'email-address',
                          'picture-url',
                          'public-profile-url']
        fields = self.get_settings().get('PROFILE_FIELDS',
                                         default_fields)
        return fields

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append('r_emailaddress')
        return scope

    def extract_common_fields(self, data):
        return dict(email=data.get('email-address'),
                    first_name=data.get('first-name'),
                    last_name=data.get('last-name'))


providers.registry.register(LinkedInOAuth2Provider)
