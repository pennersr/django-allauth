from django.conf import settings

from allauth.socialaccount import app_settings
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

    def get_login_url(self, request, **kwargs):
        return super(OpenIDConnectProvider, self).get_login_url(request, **kwargs)

    def get_callback_url(self):
        return super(OpenIDConnectProvider, self).get_callback_url()

    @property
    def server_url(self):
        return self.wk_server_url(self.base_server_url)

    @property
    def base_server_url(self):
        other_url = self.settings.get("KEYCLOAK_URL_ALT")
        if other_url is None:
            other_url = self.settings.get("KEYCLOAK_URL")
        url = "{0}/realms/{1}".format(other_url, self.settings.get("KEYCLOAK_REALM"))
        return url

    @property
    def provider_base_url(self):
        return "{0}/realms/{1}".format(
            self.settings.get("KEYCLOAK_URL"), self.settings.get("KEYCLOAK_REALM")
        )

    @property
    def settings(self):
        return app_settings.PROVIDERS.get(self.id, {})


provider_classes = [KeycloakProvider]
