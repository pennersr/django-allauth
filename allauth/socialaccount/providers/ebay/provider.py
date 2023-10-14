# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EBayAccount(ProviderAccount):
    # def get_avatar_url(self):
    #     return self.account.extra_data.get("picture")

    # def to_str(self):
    #     dflt = super(EBayAccount, self).to_str()
    #     return self.account.extra_data.get("name", dflt)
    pass


class EBayProvider(OAuth2Provider):
    id = "ebay"
    name = "eBay"
    account_class = EBayAccount

    # def get_default_scope(self):
    #     return ["openid", "profile", "email"]

    # def extract_uid(self, data):
    #     return str(data["sub"])

    # def extract_common_fields(self, data):
    #     return dict(
    #         email=data.get("email"),
    #         username=data.get("username"),
    #         name=data.get("name"),
    #     )


provider_classes = [EBayProvider]
