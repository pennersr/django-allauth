from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from allauth.compat import six
from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)

from .provider import OpenStreetMapProvider


class OpenStreetMapAPI(OAuth):

    url = 'https://www.openstreetmap.org/api/0.6/user/details'

    def get_user_info(self):
        raw_xml = self.query(self.url)
        if not six.PY3:
            raw_xml = raw_xml.encode('utf8')
        try:
            user_element = ElementTree.fromstring(raw_xml).find('user')
            user_info = user_element.attrib
            user_avatar = user_element.find('img')
            if user_avatar is not None:
                user_info.update({'avatar': user_avatar.attrib.get('href')})
            return user_info
        except (ExpatError, KeyError, IndexError):
            return None


class OpenStreetMapOAuthAdapter(OAuthAdapter):
    provider_id = OpenStreetMapProvider.id
    request_token_url = 'https://www.openstreetmap.org/oauth/request_token'
    access_token_url = 'https://www.openstreetmap.org/oauth/access_token'
    authorize_url = 'https://www.openstreetmap.org/oauth/authorize'

    def complete_login(self, request, app, token, response):
        client = OpenStreetMapAPI(request, app.client_id, app.secret,
                                  self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth_login = OAuthLoginView.adapter_view(OpenStreetMapOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(OpenStreetMapOAuthAdapter)
