"""
Views for PatreonProvider
https://www.patreon.com/platform/documentation/oauth
"""

import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import PatreonProvider


class PatreonOAuth2Adapter(OAuth2Adapter):
    provider_id = PatreonProvider.id
    access_token_url = 'https://www.patreon.com/api/oauth2/token'
    authorize_url = 'https://www.patreon.com/oauth2/authorize'
    profile_url = 'https://www.patreon.com/api/oauth2/v2/identity?include=memberships&fields%5Buser%5D=email,first_name,full_name,image_url,last_name,social_connections,thumb_url,url,vanity'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            headers={'Authorization': 'Bearer ' + token.token})
        extra_data = resp.json().get('data')

        try:
            member_id = extra_data['relationships']['memberships']['data'][0]['id']
            member_url = f'https://www.patreon.com/api/oauth2/v2/members/{member_id}?include=currently_entitled_tiers&fields%5Btier%5D=title'
            resp_member = requests.get(member_url,
                                headers={'Authorization': 'Bearer ' + token.token})
            pledge_title = resp_member.json()['included'][0]['attributes']['title']
            extra_data["pledge_level"] = pledge_title

        except (KeyError, IndexError):
            extra_data["pledge_level"] = None
            pass
            
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PatreonOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PatreonOAuth2Adapter)
