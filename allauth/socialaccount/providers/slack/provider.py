from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class SlackAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('user').get('image_192', None)

    def to_str(self):
        dflt = super(SlackAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class SlackProvider(OAuth2Provider):
    id = 'slack'
    name = 'Slack'
    account_class = SlackAccount

    def extract_uid(self, data):
        return "%s_%s" % (str(data.get('team').get('id')),
                          str(data.get('user').get('id')))

    def extract_common_fields(self, data):
        return dict(name=data.get('name'),
                    email=data.get('user').get('email', None))

    def get_default_scope(self):
        return ['identity.basic', 'identity.email',
                'identity.avatar', 'identity.team']


providers.registry.register(SlackProvider)
