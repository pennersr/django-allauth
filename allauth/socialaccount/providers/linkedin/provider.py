from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider

from allauth.socialaccount import app_settings

class LinkedInAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('public-profile-url')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture-url')
        
    def to_str(self):
        dflt = super(LinkedInAccount, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        first_name = self.account.extra_data.get('first-name', None)
        last_name = self.account.extra_data.get('last-name', None)
        if first_name and last_name:
            name = first_name+' '+last_name
        return name


class LinkedInProvider(OAuthProvider):
    id = 'linkedin'
    name = 'LinkedIn'
    package = 'allauth.socialaccount.providers.linkedin'
    account_class = LinkedInAccount

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append('r_emailaddress')
        return scope

providers.registry.register(LinkedInProvider)
