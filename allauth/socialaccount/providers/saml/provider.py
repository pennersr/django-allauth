from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount


class SAMLAccount(ProviderAccount):
    def to_str(self):
        return super().to_str()


class SAMLProvider(Provider):
    id = "saml"
    account_class = SAMLAccount

    @property
    def name(self):
        return self.app.name or self.app.client_id or self.id

    def get_login_url(self, request, **kwargs):
        url = reverse("saml_login", kwargs={"organization_slug": self.app.client_id})
        if kwargs:
            url = url + "?" + urlencode(kwargs)
        return url

    def extract_extra_data(self, data):
        return data.get_attributes()

    def extract_uid(self, data):
        """
        The `uid` is not unique across different SAML IdP's. Therefore,
        we're using a fully qualified ID: <uid>@<entity_id>.
        """
        uid = self._extract(data)["uid"]
        entity_id = self.app.provider_id
        fq_uid = f"{uid}@{entity_id}"
        return fq_uid

    def extract_common_fields(self, data):
        ret = self._extract(data)
        ret.pop("uid", None)
        return ret

    def _extract(self, data):
        provider_config = self.app.settings
        raw_attributes = data.get_attributes()
        attributes = {}
        attribute_mapping = provider_config["attribute_mapping"]
        # map configured provider attributes
        for key, provider_key in attribute_mapping.items():
            attribute_list = raw_attributes.get(provider_key, [""])
            attributes[key] = attribute_list[0] if len(attribute_list) > 0 else ""

        # TODO email_verified 'true' -> True
        return attributes


provider_classes = [SAMLProvider]
