# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EbayAccount(ProviderAccount):
    def to_str(self):
        default = super(EbayAccount, self).to_str()
        return self.account.extra_data.get("name", default)


class EbayProvider(OAuth2Provider):
    id = "ebay"
    name = "EBay"
    account_class = EbayAccount

    def get_default_scope(self):
        return ["https://api.ebay.com/oauth/api_scope"]

    def extract_uid(self, data):
        return str(data.get("userid"))

    def extract_common_fields(self, data):
        return dict(email=data.get("email"), username=data.get("username"))


provider_classes = [EbayProvider]
