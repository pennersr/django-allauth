from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MailRuAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        ret = None
        if self.account.extra_data.get('has_pic'):
            pic_big_url = self.account.extra_data.get('pic_big')
            pic_small_url = self.account.extra_data.get('pic_small')
            if pic_big_url:
                return pic_big_url
            elif pic_small_url:
                return pic_small_url
        else:
            return ret

    def to_str(self):
        dflt = super(MailRuAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class MailRuProvider(OAuth2Provider):
    id = 'mailru'
    name = 'Mail.RU'
    package = 'allauth.socialaccount.providers.mailru'
    account_class = MailRuAccount

    def extract_uid(self, data):
        return data['uid']

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('last_name'),
                    username=data.get('nick'),
                    first_name=data.get('first_name'))


providers.registry.register(MailRuProvider)
