import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from allauth.socialaccount.models import SocialLogin, SocialAccount
from allauth.socialaccount.adapter import get_adapter

from provider import GoogleProvider

class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    profile_url = 'https://www.googleapis.com/oauth2/v1/userinfo'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={ 'access_token': token.token,
                                     'alt': 'json' })
        extra_data = resp.json()
        # extra_data is something of the form:
        # 
        # {u'family_name': u'Penners', u'name': u'Raymond Penners', 
        #  u'picture': u'https://lh5.googleusercontent.com/-GOFYGBVOdBQ/AAAAAAAAAAI/AAAAAAAAAGM/WzRfPkv4xbo/photo.jpg', 
        #  u'locale': u'nl', u'gender': u'male', 
        #  u'email': u'raymond.penners@gmail.com', 
        #  u'link': u'https://plus.google.com/108204268033311374519', 
        #  u'given_name': u'Raymond', u'id': u'108204268033311374519', 
        #  u'verified_email': True}
        #
        # TODO: We could use verified_email to bypass allauth email verification
        uid = str(extra_data['id'])
        user = get_adapter() \
            .populate_new_user(email=extra_data.get('email'),
                               last_name=extra_data.get('family_name'),
                               first_name=extra_data.get('given_name'))
        email_addresses = []
        if user.email and extra_data.get('verified_email'):
            email_addresses.append(EmailAddress(email=user.email,
                                                verified=True,
                                                primary=True))
        account = SocialAccount(extra_data=extra_data,
                                uid=uid,
                                provider=self.provider_id,
                                user=user)
        return SocialLogin(account,
                           email_addresses=email_addresses)

oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)

