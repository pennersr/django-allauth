# -*- coding: utf-8 -*-
from django.conf import settings

from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProvider,
    OpenIDConnectProviderAccount,
)


OVERRIDE_NAME = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("keycloak", {})
    .get("OVERRIDE_NAME", "Keycloak")
)


class KeycloakAccount(OpenIDConnectProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("picture")


class KeycloakProvider(OpenIDConnectProvider):
    id = "keycloak"
    name = OVERRIDE_NAME
    account_class = KeycloakAccount


provider_classes = [KeycloakProvider]
