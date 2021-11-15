from __future__ import unicode_literals

import json
import requests

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import MicrosoftGraphProvider


def _check_errors(response):
    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        raise OAuth2Error(
            "Invalid JSON from Microsoft Graph API: {}".format(response.text)
        )

    if "id" not in data:
        error_message = "Error retrieving Microsoft profile"
        microsoft_error_message = data.get("error", {}).get("message")
        if microsoft_error_message:
            error_message = ": ".join((error_message, microsoft_error_message))
        raise OAuth2Error(error_message)

    return data


class MicrosoftGraphOAuth2Adapter(OAuth2Adapter):
    provider_id = MicrosoftGraphProvider.id

    def __init__(self, request):
        super(MicrosoftGraphOAuth2Adapter, self).__init__(request)
        provider = self.get_provider()
        tenant = provider.get_settings().get("tenant") or "common"
        user_properties = (
            "businessPhones",
            "displayName",
            "givenName",
            "id",
            "jobTitle",
            "mail",
            "mobilePhone",
            "officeLocation",
            "preferredLanguage",
            "surname",
            "userPrincipalName",
            "mailNickname",
        )
        base_url = "https://login.microsoftonline.com/{0}".format(tenant)
        self.access_token_url = "{0}/oauth2/v2.0/token".format(base_url)
        self.authorize_url = "{0}/oauth2/v2.0/authorize".format(base_url)
        self.profile_url = "https://graph.microsoft.com/v1.0/me/"
        self.profile_url_params = {"$select": ",".join(user_properties)}

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        response = requests.get(
            self.profile_url, self.profile_url_params, headers=headers
        )
        extra_data = _check_errors(response)
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MicrosoftGraphOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MicrosoftGraphOAuth2Adapter)
