import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import OrcidProvider


class OrcidOAuth2Adapter(OAuth2Adapter):
    provider_id = OrcidProvider.id
    # http://support.orcid.org/knowledgebase/articles/335483-the-public-
    # client-orcid-api

    member_api_default = False
    base_domain_default = 'orcid.org'

    settings = app_settings.PROVIDERS.get(provider_id, {})

    base_domain = settings.get('BASE_DOMAIN', base_domain_default)
    member_api = settings.get('MEMBER_API', member_api_default)

    api_domain = '{0}.{1}'.format('api' if member_api else 'pub', base_domain)

    authorize_url = 'https://{0}/oauth/authorize'.format(base_domain)
    access_token_url = 'https://{0}/oauth/token'.format(api_domain)
    profile_url = 'https://{0}/v1.2/%s/orcid-profile'.format(api_domain)

    def complete_login(self, request, app, token, **kwargs):
        params = {}
        if self.member_api:
            params['access_token'] = token.token

        resp = requests.get(self.profile_url % kwargs['response']['orcid'],
                            params=params,
                            headers={'accept': 'application/orcid+json'})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(OrcidOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(OrcidOAuth2Adapter)
