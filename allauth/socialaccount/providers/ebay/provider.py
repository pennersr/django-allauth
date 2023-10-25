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
        common_fields = {
            "userId": data.get("userId"),
            "username": data.get("username"),
            "accountType": data.get("accountType"),
        }

        account_type = data.get("accountType")
        if account_type == "BUSINESS":
            common_fields["email"] = data.get("businessAccount", {}).get("email")
        elif account_type == "INDIVIDUAL":
            common_fields["email"] = data.get("individualAccount", {}).get("email")

        return common_fields


provider_classes = [EbayProvider]
