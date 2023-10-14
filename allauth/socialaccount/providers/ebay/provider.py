# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class EBayAccount(ProviderAccount):
    pass


class EBayProvider(OAuth2Provider):
    id = "ebay"
    name = "eBay"
    account_class = EBayAccount

    def extract_uid(self, data):
        # NOTE: Ensure that the user_id exists
        return str(data.get("userid"))


provider_classes = [EBayProvider]
