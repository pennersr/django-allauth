from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class TumblrAccount(ProviderAccount):
    def get_profile_url_(self):
        return 'http://%s.tumblr.com/' \
            % self.account.extra_data.get('name')

    def to_str(self):
        dflt = super(TumblrAccount, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        return name


class TumblrProvider(OAuthProvider):
    id = 'tumblr'
    name = 'Tumblr'
    package = 'allauth.socialaccount.providers.tumblr'
    account_class = TumblrAccount

    def extract_uid(self, data):
        return data['name']

    def extract_common_fields(self, data):
        return dict(first_name=data.get('name'),)


providers.registry.register(TumblrProvider)
