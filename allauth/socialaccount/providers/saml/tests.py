from unittest.mock import patch

from django.urls import reverse
from django.utils.http import urlencode

import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.saml.utils import build_saml_config


def test_acs(client, db, saml_settings, acs_saml_response, mocked_signature_validation):
    data = {"SAMLResponse": acs_saml_response}
    resp = client.post(
        reverse("saml_acs", kwargs={"organization_slug": "org"}), data=data
    )
    finish_url = reverse("saml_finish_acs", kwargs={"organization_slug": "org"})
    assert resp.status_code == 302
    assert resp["location"] == finish_url
    resp = client.get(finish_url)
    assert resp["location"] == "/accounts/profile/"
    account = SocialAccount.objects.get(
        provider="urn:dev-123.us.auth0.com", uid="dummysamluid"
    )

    email = EmailAddress.objects.get(user=account.user)
    assert email.email == "john.doe@email.org"


def test_acs_error(client, db, saml_settings):
    data = {"SAMLResponse": "bad-response"}
    resp = client.post(
        reverse("saml_acs", kwargs={"organization_slug": "org"}), data=data
    )
    assert resp.status_code == 200
    assert "socialaccount/authentication_error.html" in (t.name for t in resp.templates)


def test_login(
    client,
    db,
    saml_settings,
):
    resp = client.get(reverse("saml_login", kwargs={"organization_slug": "org"}))
    assert resp.status_code == 302
    assert resp["location"].startswith(
        "https://dev-123.us.auth0.com/samlp/456?SAMLRequest="
    )


def test_metadata(
    client,
    db,
    saml_settings,
):
    resp = client.get(reverse("saml_metadata", kwargs={"organization_slug": "org"}))
    assert resp.status_code == 200
    assert resp.content.startswith(
        b'<?xml version="1.0"?>\n<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata'
    )


def test_sls(auth_client, db, saml_settings, user_factory, sls_saml_request):
    with patch("allauth.account.adapter.DefaultAccountAdapter.logout") as logout_mock:
        resp = auth_client.get(
            reverse("saml_sls", kwargs={"organization_slug": "org"})
            + "?"
            + urlencode({"SAMLRequest": sls_saml_request})
        )
        assert logout_mock.call_count == 1
    assert resp.status_code == 302
    assert resp["location"].startswith(
        "https://dev-123.us.auth0.com/samlp/456?SAMLResponse="
    )


@pytest.mark.parametrize(
    "provider_config",
    [
        {
            "idp": {
                "entity_id": "dummy",
                "sso_url": "https://idp.org/sso/",
                "slo_url": "https://idp.saml.org/slo/",
                "x509cert": "cert",
            }
        },
    ],
)
def test_build_saml_config_without_metadata_url(rf, provider_config):
    request = rf.get("/")
    config = build_saml_config(request, provider_config, "org")
    assert config["idp"]["entityId"] == "dummy"
    assert config["idp"]["x509cert"] == "cert"
    assert config["idp"]["singleSignOnService"] == {"url": "https://idp.org/sso/"}
    assert config["idp"]["singleLogoutService"] == {"url": "https://idp.saml.org/slo/"}


@pytest.mark.parametrize(
    "provider_config",
    [
        {
            "idp": {
                "entity_id": "dummy",
                "metadata_url": "https://idp.org/sso/",
            }
        },
    ],
)
def test_build_saml_config(rf, provider_config):
    request = rf.get("/")
    with patch(
        "onelogin.saml2.idp_metadata_parser.OneLogin_Saml2_IdPMetadataParser.parse_remote"
    ) as parse_mock:
        parse_mock.return_value = {
            "idp": {
                "entityId": "dummy",
                "singleSignOnService": {"url": "https://idp.org/sso/"},
                "singleLogoutService": {"url": "https://idp.saml.org/slo/"},
                "x509cert": "cert",
            }
        }
        config = build_saml_config(request, provider_config, "org")

    assert config["idp"]["entityId"] == "dummy"
    assert config["idp"]["x509cert"] == "cert"
    assert config["idp"]["singleSignOnService"] == {"url": "https://idp.org/sso/"}
    assert config["idp"]["singleLogoutService"] == {"url": "https://idp.saml.org/slo/"}
