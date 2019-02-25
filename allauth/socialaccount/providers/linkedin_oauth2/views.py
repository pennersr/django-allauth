import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import LinkedInOAuth2Provider


class LinkedInOAuth2Adapter(OAuth2Adapter):
    provider_id = LinkedInOAuth2Provider.id
    access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    authorize_url = 'https://www.linkedin.com/oauth/v2/authorization'
    profile_url = 'https://api.linkedin.com/v2/me'
    email_url = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'  # noqa

    # See:
    # http://developer.linkedin.com/forum/unauthorized-invalid-or-expired-token-immediately-after-receiving-oauth2-token?page=1 # noqa
    access_token_method = 'GET'

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_user_info(token)
        return self.get_provider().sociallogin_from_response(
            request, extra_data)

    def get_user_info(self, token):
        fields = self.get_provider().get_profile_fields()
        target_profile_url = self.profile_url + '?projection=(%s)' % ','.join(fields)

        headers = {}
        headers.update(self.get_provider().get_settings().get('HEADERS', {}))
        headers['Authorization'] = ' '.join(['Bearer', token.token])

        profile_resp = requests.get(target_profile_url, headers=headers)
        profile_resp.raise_for_status()
        profile_resp_json = profile_resp.json()

        email_resp = requests.get(self.email_url, headers=headers)
        email_resp.raise_for_status()
        email_resp_json = email_resp.json()

        merged = profile_resp_json.copy()
        merged.update(email_resp_json)

        return merged


oauth2_login = OAuth2LoginView.adapter_view(LinkedInOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LinkedInOAuth2Adapter)
