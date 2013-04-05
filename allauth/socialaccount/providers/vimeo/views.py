from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.adapter import get_adapter

from pprint import pprint

from provider import VimeoProvider

class VimeoAPI(OAuth):
    url = 'http://vimeo.com/api/rest/v2?method=vimeo.people.getInfo'

    def get_user_info(self):
        url = self.url
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
            attributes = {}
            for key, val in xml.attrib.items():
                attributes[key] = val
            return { 'attributes': attributes, 'text': xml.text }
        else:
            out = {}
            attributes = {}
            for key, val in xml.attrib.items():
                attributes[key] = val
            out = { 'attributes': attributes }

            for node in xml.getchildren():
                if node.tag in out:
                    if not isinstance(out[node.tag], list):
                        out[node.tag] = [out[node.tag]]
                    out[node.tag].append(self.to_dict(node))
                else:
                    out[node.tag] = self.to_dict(node)
            return out

class VimeoOAuthAdapter(OAuthAdapter):
    provider_id = VimeoProvider.id
    request_token_url = 'https://vimeo.com/oauth/request_token'
    access_token_url = 'https://vimeo.com/oauth/access_token'
    authorize_url = 'https://vimeo.com/oauth/authorize'

    def complete_login(self, request, app, token):
        client = VimeoAPI(request, app.client_id, app.secret,
                             self.request_token_url)
        extra_data = client.get_user_info()
        uid = extra_data.get('person').get('attributes').get('id')
        first_name = extra_data.get('person').get('display_name').get('text').split(None, 1)[0]
        last_name = extra_data.get('person').get('display_name').get('text').rsplit(None, 1)[1]
        user = get_adapter() \
            .populate_new_user(first_name=first_name, last_name = last_name)
        account = SocialAccount(user=user,
                                provider=self.provider_id,
                                extra_data=extra_data,
                                uid=uid)
        return SocialLogin(account)

oauth_login = OAuthLoginView.adapter_view(VimeoOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(VimeoOAuthAdapter)
