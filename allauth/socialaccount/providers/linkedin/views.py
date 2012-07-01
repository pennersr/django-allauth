from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from django.contrib.auth.models import User

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount.models import SocialAccount, SocialLogin

from provider import LinkedInProvider


class LinkedInAPI(OAuth):
    url = 'https://api.linkedin.com/v1/people/~'
    fields = ['id', 'first-name', 'last-name']

    def get_user_info(self):
        url = self.url + ':(%s)' % ','.join(self.fields)
        raw_xml = self.query(url)
        try:
            return self.to_dict(ElementTree.fromstring(raw_xml))
        except (ExpatError, KeyError, IndexError):
            return None

    def to_dict(self, xml):
        """
        Convert XML structure to dict recursively, repeated keys
        entries are returned as in list containers.
        """
        children = xml.getchildren()
        if not children:
            return xml.text
        else:
            out = {}
            for node in xml.getchildren():
                if node.tag in out:
                    if not isinstance(out[node.tag], list):
                        out[node.tag] = [out[node.tag]]
                    out[node.tag].append(self.to_dict(node))
                else:
                    out[node.tag] = self.to_dict(node)
            return out


class LinkedInOAuthAdapter(OAuthAdapter):
    provider_id = LinkedInProvider.id
    request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
    access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken'
    authorize_url = 'https://www.linkedin.com/uas/oauth/authenticate'

    def complete_login(self, request, app, token):
        client = LinkedInAPI(request, app.key, app.secret,
                             self.request_token_url)
        extra_data = client.get_user_info()
        uid = extra_data['id']
        user = User(first_name=extra_data.get('first-name', ''),
                    last_name=extra_data.get('last-name', ''))
        account = SocialAccount(user=user,
                                provider=self.provider_id,
                                extra_data=extra_data,
                                uid=uid)
        return SocialLogin(account)

oauth_login = OAuthLoginView.adapter_view(LinkedInOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(LinkedInOAuthAdapter)

