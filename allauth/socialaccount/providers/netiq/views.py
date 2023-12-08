# -*- coding: utf-8 -*-
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.netiq.provider import NetIQProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class NetIQOAuth2Adapter(OAuth2Adapter):
    provider_id = NetIQProvider.id
    supports_state = True

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("NETIQ_URL")

    @property
    def access_token_url(self):
        return "{}/nidp/oauth/nam/token".format(self.provider_base_url)

    @property
    def authorize_url(self):
        return "{}/nidp/oauth/nam/authz".format(self.provider_base_url)

    @property
    def userinfo_url(self):
        return "{}/nidp/oauth/nam/userinfo".format(self.provider_base_url)

    def complete_login(self, request, app, token, **kwargs):
        """
        Get the user info from userinfo endpoint and return a
        A populated instance of the `SocialLogin` model (unsaved)
        :param request:
        :param app:
        :param token:
        :param kwargs:
        :return:
        """

        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.userinfo_url,
                headers={"Authorization": "Bearer {}".format(token.token)},
            )
        )

        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(NetIQOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(NetIQOAuth2Adapter)
