from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount


class SAMLAccount(ProviderAccount):
    def to_str(self):
        return super().to_str()


class SAMLProvider(Provider):
    id = "saml"
    name = "SAML"
    account_class = SAMLAccount
    default_attribute_mapping = {
        "uid": [
            "http://schemas.auth0.com/clientID",
            "urn:oasis:names:tc:SAML:attribute:subject-id",
        ],
        "email": [
            "urn:oid:0.9.2342.19200300.100.1.3",
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        ],
        "email_verified": [
            "http://schemas.auth0.com/email_verified",
        ],
        "first_name": [
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
            "urn:oid:2.5.4.42",
        ],
        "last_name": [
            "urn:oid:2.5.4.4",
        ],
        "username": [
            "http://schemas.auth0.com/nickname",
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.app.name or self.app.client_id or self.name

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
        return self._extract(data)["uid"]

    def extract_common_fields(self, data):
        ret = self._extract(data)
        ret.pop("uid", None)
        return ret

    def _extract(self, data):
        provider_config = self.app.settings
        raw_attributes = data.get_attributes()
        attributes = {}
        attribute_mapping = provider_config.get(
            "attribute_mapping", self.default_attribute_mapping
        )
        # map configured provider attributes
        for key, provider_keys in attribute_mapping.items():
            if isinstance(provider_keys, str):
                provider_keys = [provider_keys]
            for provider_key in provider_keys:
                attribute_list = raw_attributes.get(provider_key, [""])
                if len(attribute_list) > 0:
                    attributes[key] = attribute_list[0]
                    break
        email_verified = attributes.get("email_verified")
        if email_verified:
            email_verified = email_verified.lower() in ["true", "1", "t", "y", "yes"]
            attributes["email_verified"] = email_verified
        return attributes


provider_classes = [SAMLProvider]
