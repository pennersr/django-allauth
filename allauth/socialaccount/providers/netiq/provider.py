# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class NetIQAccount(ProviderAccount):
    def to_str(self):
        dflt = super(NetIQAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class NetIQProvider(OAuth2Provider):
    id = "netiq"
    name = "NetIQ"
    account_class = NetIQAccount

    def get_default_scope(self):
        return ["openid", "profile", "email"]

    def extract_uid(self, data):
        return str(data["preferred_username"])

    def extract_extra_data(self, data):
        return data

    def extract_common_fields(self, data):
        return dict(
            email=data["email"],
            last_name=data["family_name"],
            first_name=data["given_name"],
        )


provider_classes = [NetIQProvider]
