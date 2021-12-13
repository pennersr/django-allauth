# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class GumroadAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("url")

    def to_str(self):
        dflt = super(GumroadAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class GumroadProvider(OAuth2Provider):
    id = "gumroad"
    name = "Gumroad"
    account_class = GumroadAccount

    def get_default_scope(self):
        return ["edit_products"]

    def extract_uid(self, data):
        return str(data["user_id"])

    def extract_common_fields(self, data):
        try:
            username = data["url"].split("https://gumroad.com/")[1]
        except (KeyError, IndexError, AttributeError):
            username = None
        return dict(
            username=username,
            email=data.get("email"),
            name=data.get("name"),
            twitter_handle=data.get("twitter_handle"),
            url=data.get("url"),
        )


provider_classes = [GumroadProvider]
