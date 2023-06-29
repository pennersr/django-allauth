from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)

from .provider import LinkedInProvider


class LinkedInAPI(OAuth):
    url = "https://api.linkedin.com/v1/people/~"

    def get_user_info(self):
        adapter = get_adapter(self.request)
        provider = adapter.get_provider(self.request, LinkedInProvider.id)
        fields = provider.get_profile_fields()
        url = self.url + ":(%s)" % ",".join(fields)
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
        children = list(xml)
        if not children:
            return xml.text
        else:
            out = {}
            for node in list(xml):
                if node.tag in out:
                    if not isinstance(out[node.tag], list):
                        out[node.tag] = [out[node.tag]]
                    out[node.tag].append(self.to_dict(node))
                else:
                    out[node.tag] = self.to_dict(node)
            return out


class LinkedInOAuthAdapter(OAuthAdapter):
    provider_id = LinkedInProvider.id
    request_token_url = "https://api.linkedin.com/uas/oauth/requestToken"
    access_token_url = "https://api.linkedin.com/uas/oauth/accessToken"
    authorize_url = "https://www.linkedin.com/uas/oauth/authenticate"

    def complete_login(self, request, app, token, response):
        client = LinkedInAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth_login = OAuthLoginView.adapter_view(LinkedInOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(LinkedInOAuthAdapter)
