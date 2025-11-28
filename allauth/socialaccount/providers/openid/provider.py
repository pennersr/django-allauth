from urllib.parse import urlparse

from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount

from .utils import (
    AXAttribute,
    OldAXAttribute,
    SRegField,
    get_email_from_response,
    get_value_from_response,
)


class OpenIDAccount(ProviderAccount):
    def get_brand(self):
        ret = super(OpenIDAccount, self).get_brand()
        domain = urlparse(self.account.uid).netloc
        provider_map = {}
        for d, p in provider_map.items():
            if domain.lower().find(d) >= 0:
                ret = p
                break
        return ret

    def to_str(self):
        return self.account.uid


class OpenIDProvider(Provider):
    id = "openid"
    name = "OpenID"
    account_class = OpenIDAccount
    uses_apps = False

    def get_login_url(self, request, **kwargs):
        url = reverse("openid_login")
        if kwargs:
            url += f"?{urlencode(kwargs)}"
        return url

    def get_brands(self):
        default_servers = []
        return self.get_settings().get("SERVERS", default_servers)

    def get_server_settings(self, endpoint):
        servers = self.get_settings().get("SERVERS", [])
        for server in servers:
            if endpoint is not None and endpoint.startswith(server.get("openid_url")):
                return server
        return {}

    def extract_extra_data(self, response):
        extra_data = {}
        server_settings = self.get_server_settings(response.endpoint.server_url)
        extra_attributes = server_settings.get("extra_attributes", [])
        for attribute_id, name, _ in extra_attributes:
            extra_data[attribute_id] = get_value_from_response(
                response, ax_names=[name]
            )
        return extra_data

    def extract_uid(self, response):
        return response.identity_url

    def extract_common_fields(self, response):
        first_name = (
            get_value_from_response(
                response,
                ax_names=[
                    AXAttribute.PERSON_FIRST_NAME,
                    OldAXAttribute.PERSON_FIRST_NAME,
                ],
            )
            or ""
        )
        last_name = (
            get_value_from_response(
                response,
                ax_names=[
                    AXAttribute.PERSON_LAST_NAME,
                    OldAXAttribute.PERSON_LAST_NAME,
                ],
            )
            or ""
        )
        name = (
            get_value_from_response(
                response,
                sreg_names=[SRegField.NAME],
                ax_names=[AXAttribute.PERSON_NAME, OldAXAttribute.PERSON_NAME],
            )
            or ""
        )
        return dict(
            email=get_email_from_response(response),
            first_name=first_name,
            last_name=last_name,
            name=name,
        )


provider_classes = [OpenIDProvider]
