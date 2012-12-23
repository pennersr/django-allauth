from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount.providers.oauth2.client import OAuth2Error

from allauth.socialaccount import requests
from allauth.socialaccount.models import SocialLogin, SocialAccount
from allauth.utils import get_user_model

from django.conf import settings

from provider import StackExchangeProvider

User = get_user_model()

class StackExchangeOAuth2Adapter(OAuth2Adapter):
    provider_id = StackExchangeProvider.id
    access_token_url = 'https://stackexchange.com/oauth/access_token'
    authorize_url = 'https://stackexchange.com/oauth/'
    profile_url = 'https://api.stackexchange.com/2.1/me'

    def complete_login(self, request, app, token):
        resp = requests.get(self.profile_url,
                            {
                                'access_token': token.token,
                                'key': settings.STACKEXCHANGE_KEYS[int(app.key)][0],
                                'site': settings.STACKEXCHANGE_KEYS[int(app.key)][1]
                            })
        extra_data = resp.json
        # extra_data is something of the form:
        #
        # {
        #   "items": [
        #     {
        #       "user_id": 654321,
        #       "user_type": "registered",
        #       "creation_date": 1234567890,
        #       "display_name": "Alice",
        #       "profile_image": "http://www.my-site.com/my-handsome-face.jpg",
        #       "reputation": 44,
        #       "reputation_change_day": 0,
        #       "reputation_change_week": 0,
        #       "reputation_change_month": 0,
        #       "reputation_change_quarter": 15,
        #       "reputation_change_year": 31,
        #       "age": 30,
        #       "last_access_date": 1355724123,
        #       "last_modified_date": 1332302654,
        #       "is_employee": false,
        #       "link": "http://stackoverflow.com/users/654321/alice",
        #       "website_url": "http://twitter.com/alice",
        #       "location": "Japan",
        #       "account_id": 123456,
        #       "badge_counts": {
        #         "gold": 0,
        #         "silver": 0,
        #         "bronze": 6
        #       },
        #       "accept_rate": 100
        #     }
        #   ],
        #   "quota_remaining": 9997,
        #   "quota_max": 10000,
        #   "has_more": false
        # }
        if len(extra_data['items']) > 0:
            uid = str(extra_data['items'][0]['user_id'])
            user = User(username=extra_data['items'][0]['display_name'])
            account = SocialAccount(extra_data=extra_data,
                                    uid=uid,
                                    provider=self.provider_id,
                                    user=user)
            return SocialLogin(account)
        else:
            raise OAuth2Error("stackexchange/no_site_profile_error.html",
                              { 'se_site': settings.STACKEXCHANGE_KEYS[int(app.key)][1] })

oauth2_login = OAuth2LoginView.adapter_view(StackExchangeOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(StackExchangeOAuth2Adapter)

