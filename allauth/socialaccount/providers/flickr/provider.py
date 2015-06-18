from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class FlickrAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data \
            .get('person').get('profileurl').get('_content')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture-url')

    def to_str(self):
        dflt = super(FlickrAccount, self).to_str()
        name = self.account.extra_data \
            .get('person').get('realname').get('_content', dflt)
        return name


class FlickrProvider(OAuthProvider):
    id = 'flickr'
    name = 'Flickr'
    package = 'allauth.socialaccount.providers.flickr'
    account_class = FlickrAccount

    def get_default_scope(self):
        scope = []
        return scope

    def get_auth_params(self, request, action):
        ret = super(FlickrProvider, self).get_auth_params(request,
                                                          action)
        if 'perms' not in ret:
            ret['perms'] = 'read'
        return ret

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

    def extract_uid(self, data):
        return data['person']['nsid']

    def extract_common_fields(self, data):
        person = data.get('person', {})
        name = person.get('realname', {}).get('_content')
        username = person.get('username', {}).get('_content')
        return dict(email=data.get('email-address'),
                    name=name,
                    username=username)


providers.registry.register(FlickrProvider)
