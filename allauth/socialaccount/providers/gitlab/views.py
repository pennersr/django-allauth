# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


def _check_errors(response):
    #  403 error's are presented as user-facing errors
    if response.status_code == 403:
        msg = response.content
        raise OAuth2Error("Invalid data from GitLab API: %r" % (msg))

    try:
        data = response.json()
    except ValueError:  # JSONDecodeError on py3
        raise OAuth2Error("Invalid JSON from GitLab API: %r" % (response.text))

    if response.status_code >= 400 or "error" in data:
        # For errors, we expect the following format:
        # {"error": "error_name", "error_description": "Oops!"}
        # For example, if the token is not valid, we will get:
        # {"message": "status_code - message"}
        error = data.get("error", "") or response.status_code
        desc = data.get("error_description", "") or data.get("message", "")

        raise OAuth2Error("GitLab error: %s (%s)" % (error, desc))

    # The expected output from the API follows this format:
    # {"id": 12345, ...}
    if "id" not in data:
        # If the id is not present, the output is not usable (no UID)
        raise OAuth2Error("Invalid data from GitLab API: %r" % (data))

    return data


class GitLabOAuth2Adapter(OAuth2Adapter):
    provider_id = GitLabProvider.id
    provider_default_url = "https://gitlab.com"
    provider_api_version = "v4"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("GITLAB_URL", provider_default_url)

    access_token_url = "{0}/oauth/token".format(provider_base_url)
    authorize_url = "{0}/oauth/authorize".format(provider_base_url)
    profile_url = "{0}/api/{1}/user".format(provider_base_url, provider_api_version)

    def complete_login(self, request, app, token, response):
        response = requests.get(self.profile_url, params={"access_token": token.token})
        data = _check_errors(response)
        return self.get_provider().sociallogin_from_response(request, data)


oauth2_login = OAuth2LoginView.adapter_view(GitLabOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GitLabOAuth2Adapter)
