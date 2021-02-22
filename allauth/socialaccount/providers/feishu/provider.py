# -*- coding: utf-8 -*-

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FeishuAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_big")

    def to_str(self):
        return self.account.extra_data.get("name", super(FeishuAccount, self).to_str())


class FeishuProvider(OAuth2Provider):
    id = "feishu"
    name = "feishu"
    account_class = FeishuAccount

    def extract_uid(self, data):
        return data["open_id"]

    def extract_common_fields(self, data):
        return dict(username=data.get("name"), name=data.get("name"))


provider_classes = [FeishuProvider]
