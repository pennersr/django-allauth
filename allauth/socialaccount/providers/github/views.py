import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import GitHubProvider
from allauth.socialaccount import app_settings

GITHUB_HOST = app_settings.PROVIDERS.get('github', {}).get('GITHUB_HOST', 'github.com')
GITHUB_HOST_PROTOCOL = app_settings.PROVIDERS.get('github', {}).get('GITHUB_HOST_PROTOCOL', 'https')

URL_BASE = '%s://%s' % (GITHUB_HOST_PROTOCOL, GITHUB_HOST)
API_URL_BASE = '%s/api/v3' % URL_BASE

class GitHubOAuth2Adapter(OAuth2Adapter):
    provider_id = GitHubProvider.id
    access_token_url = '%s/login/oauth/access_token' % URL_BASE
    authorize_url = '%s/login/oauth/authorize' % URL_BASE
    profile_url = '%s/user' % API_URL_BASE
    emails_url = '%s/user/emails' % API_URL_BASE

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token})
        extra_data = resp.json()
        if app_settings.QUERY_EMAIL and not extra_data.get('email'):
            extra_data['email'] = self.get_email(token)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_email(self, token):
        email = None
        resp = requests.get(self.emails_url,
                            params={'access_token': token.token})
        emails = resp.json()
        if emails:
            email = emails[0]
            primary_emails = [
                e for e in emails
                if not isinstance(e, dict) or e.get('primary')
            ]
            if primary_emails:
                email = primary_emails[0]
            if isinstance(email, dict):
                email = email.get('email', '')
        return email


oauth2_login = OAuth2LoginView.adapter_view(GitHubOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GitHubOAuth2Adapter)
