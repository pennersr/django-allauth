# -*- coding: utf-8 -*-
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class KeapAccount(ProviderAccount):
    def to_str(self):
        dflt = super(KeapAccount, self).to_str()
        return self.account.extra_data.get("app_name", dflt)


class KeapProvider(OAuth2Provider):
    id = "Keap"
    name = "Keap"
    account_class = KeapAccount

    def get_default_scope(self):
        return ["full"]

    def extract_uid(self, data):
        return str(data["app_name"])

    def extract_common_fields(self, data):
        return dict(
            app_name=data.get("app_name"),
            email=data.get("email"),
            username=data.get("email"),
            first_name=data.get("given_name"),
            middle_name=data.get("middle_name"),
            last_name=data.get("family_name"),
            name=data.get("preferred_name") if data.get("preferred_name")
            else "{} {}".format(data.get("given_name", ""), data.get("family_name", "")),
        )

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [KeapProvider]
