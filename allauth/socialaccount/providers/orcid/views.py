import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import OrcidProvider


class OrcidOAuth2Adapter(OAuth2Adapter):
    provider_id = OrcidProvider.id
    # Production
    authorize_url = 'http://orcid.org/oauth/authorize'
    access_token_url = 'https://api.orcid.org/oauth/token'
    profile_url = 'https://api.orcid.org/v1.1/%s/orcid-profile'
    # Sandbox
    #authorize_url = 'https://sandbox.orcid.org/oauth/authorize'
    #access_token_url = 'https://api.sandbox.orcid.org/oauth/token'
    #profile_url = 'https://api.sandbox.orcid.org/v1.1/%s/orcid-profile'

    def parse_token(self, data):
        token = super(OrcidOAuth2Adapter, self).parse_token(data)
        token.orcid = data['orcid']
        return token

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url % token.orcid,
                            params={'access_token': token.token},
                            headers={'accept': 'application/orcid+json'})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(OrcidOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(OrcidOAuth2Adapter)