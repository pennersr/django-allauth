from django.utils.http import urlencode

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount

from allauth.compat import reverse


class DraugiemAccount(ProviderAccount):

    def get_avatar_url(self):
        ret = None
        pic_small_url = self.account.extra_data.get('img')
        pic_icon_url = self.account.extra_data.get('imgi')
        pic_medium_url = self.account.extra_data.get('imgm')
        pic_large_url = self.account.extra_data.get('imgl')
        if pic_large_url:
            return pic_large_url
        elif pic_medium_url:
            return pic_medium_url
        elif pic_icon_url:
            return pic_icon_url
        elif pic_small_url:
            return pic_small_url
        else:
            return ret

    def to_str(self):
        default = super(DraugiemAccount, self).to_str()
        name = self.account.extra_data.get('name')
        surname = self.account.extra_data.get('surnname')

        if name and surname:
            return '%s %s' % (name, surname)

        return default


class DraugiemProvider(Provider):
    id = 'draugiem'
    name = 'Draugiem'
    account_class = DraugiemAccount

    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        if kwargs:
            url = url + '?' + urlencode(kwargs)
        return url

    def extract_uid(self, data):
        return str(data['uid'])

    def extract_common_fields(self, data):
        uid = self.extract_uid(data)
        user_data = data['users'][uid]
        return dict(first_name=user_data.get('name'),
                    last_name=user_data.get('surname'))

    def extract_extra_data(self, data):
        uid = self.extract_uid(data)
        return data['users'][uid]


providers.registry.register(DraugiemProvider)
