import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import OrcidProvider


class OrcidOAuth2Adapter(OAuth2Adapter):
    provider_id = OrcidProvider.id
    # ORCID Public API (not Member API):
    # http://support.orcid.org/knowledgebase/articles/335483-the-public-
    # client-orcid-api
    authorize_url = 'https://orcid.org/oauth/authorize'
    access_token_url = 'https://pub.orcid.org/oauth/token'
    profile_url = 'https://pub.orcid.org/v1.1/%s/orcid-profile'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url % kwargs['response']['orcid'],
                            params={'access_token': token.token},
                            headers={'accept': 'application/orcid+json'})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(OrcidOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(OrcidOAuth2Adapter)