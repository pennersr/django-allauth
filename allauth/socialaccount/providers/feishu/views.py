# -*- coding: utf-8 -*-

import requests

from django.urls import reverse

from allauth.account import app_settings
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import build_absolute_uri

from .client import FeishuOAuth2Client
from .provider import FeishuProvider


class FeishuOAuth2Adapter(OAuth2Adapter):
    provider_id = FeishuProvider.id

    authorization_url = "https://open.feishu.cn/open-apis/authen/v1/index"
    access_token_url = "https://open.feishu.cn/open-apis/authen/v1/access_token"
    app_access_token_url = (
        "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
    )
    user_info_url = "https://open.feishu.cn/open-apis/authen/v1/user_info"

    @property
    def authorize_url(self):
        settings = self.get_provider().get_settings()
        url = settings.get("AUTHORIZE_URL", self.authorization_url)
        return url

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.user_info_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token.token,
            },
        )
        resp.raise_for_status()
        extra_data = resp.json()
        if extra_data["code"] != 0:
            raise OAuth2Error("Error retrieving code: %s" % resp.content)
        extra_data = extra_data["data"]

        return self.get_provider().sociallogin_from_response(request, extra_data)


class FeishuOAuth2ClientMixin(object):
    def get_client(self, request, app):
        callback_url = reverse(self.adapter.provider_id + "_callback")
        protocol = (
            self.adapter.redirect_uri_protocol or app_settings.DEFAULT_HTTP_PROTOCOL
        )
        callback_url = build_absolute_uri(request, callback_url, protocol=protocol)
        provider = self.adapter.get_provider()
        scope = provider.get_scope(request)
        client = FeishuOAuth2Client(
            request,
            app.client_id,
            app.secret,
            self.adapter.access_token_method,
            self.adapter.access_token_url,
            callback_url,
            scope,
        )
        return client


class FeishuOAuth2LoginView(FeishuOAuth2ClientMixin, OAuth2LoginView):
    pass


class FeishuOAuth2CallbackView(FeishuOAuth2ClientMixin, OAuth2CallbackView):
    pass


oauth2_login = FeishuOAuth2LoginView.adapter_view(FeishuOAuth2Adapter)
oauth2_callback = FeishuOAuth2CallbackView.adapter_view(FeishuOAuth2Adapter)
