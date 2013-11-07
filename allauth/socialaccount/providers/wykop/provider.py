from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount, Provider

import hashlib
import urllib
import base64
import wykop

from django.core.urlresolvers import reverse

class WykopAccount(ProviderAccount):
    def to_str(self):
        return self.account.uid

    def get_profile_url(self):
        return self.account.extra_data.get('url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_big')

class WykopProvider(Provider):
    id = 'wykop'
    name = 'Wykop'
    package = 'allauth.socialaccount.providers.wykop'
    account_class = WykopAccount

    def get_login_url(self, request, **kwargs):
        app = providers.registry.by_id(WykopProvider.id).get_app(request)
        settings = self.get_settings()
        redirect_Url = settings.get('REDIRECT_URL', request.get_host() + reverse('wykop_login_by_token'))
        url = 'http://' + wykop.WykopAPI._domain + '/user/connect/' + self.getKey(app)

        if redirect_Url:
            url += 'redirect/' + urllib.quote_plus(base64.b64encode(redirect_Url)) + '/'
            url += 'secure/' + hashlib.md5(app.secret + redirect_Url).hexdigest()

        return url

    def getKey(self, app):
        return 'appkey/' +  app.client_id + '/'


    def extract_uid(self, data):
        return data['login']

    def extract_common_fields(self, data):
        return dict(email=data.get('email').split(":")[0] + '@wykop.pl',
                    username=data.get('login'),
                    name=data.get('name'))


providers.registry.register(WykopProvider)
