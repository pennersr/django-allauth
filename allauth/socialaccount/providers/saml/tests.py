from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base.constants import AuthProcess
from allauth.socialaccount.providers.saml.utils import build_saml_config


@pytest.mark.parametrize(
    "idp_initiated,adv_settings,state_kwargs,relay_state, expected_url",
    [
        (False, {}, {}, "/not/here", settings.LOGIN_REDIRECT_URL),
        (False, {}, {"next": "/here"}, "/not/here", "/here"),
        (
            False,
            {},
            {"process": "connect"},
            "/not/here",
            reverse_lazy("socialaccount_connections"),
        ),
        (False, {}, {"process": "connect", "next": "/here"}, "/not/here", "/here"),
        (True, {"reject_idp_initiated_sso": False}, {}, "/set-by-idp", "/set-by-idp"),
        (
            True,
            {"reject_idp_initiated_sso": False},
            {},
            "not-a-url",
            settings.LOGIN_REDIRECT_URL,
        ),
        (True, {}, {}, "/set-by-idp", "/set-by-idp"),
    ],
)
def test_acs(
    request,
    idp_initiated,
    db,
    saml_settings,
    acs_saml_response_factory,
    mocked_signature_validation,
    expected_url,
    relay_state,
    state_kwargs,
    sociallogin_setup_state,
    adv_settings,
    settings,
):
    provider_settings = settings.SOCIALACCOUNT_PROVIDERS["saml"]["APPS"][0]["settings"]
    advanced = dict(provider_settings["advanced"])
    advanced.update(adv_settings)
    provider_settings["advanced"] = advanced
    process = state_kwargs.setdefault("process", AuthProcess.LOGIN)
    is_connect = process == AuthProcess.CONNECT
    if is_connect:
        client = request.getfixturevalue("auth_client")
        user = request.getfixturevalue("user")
    else:
        client = request.getfixturevalue("client")
        user = None

    state_id = None
    if not idp_initiated:
        state_id = sociallogin_setup_state(client, **state_kwargs)

    data = {"SAMLResponse": acs_saml_response_factory(in_response_to=state_id)}
    if relay_state is not None:
        data["RelayState"] = relay_state
    resp = client.post(
        reverse("saml_acs", kwargs={"organization_slug": "org"}), data=data
    )
    finish_url = reverse("saml_finish_acs", kwargs={"organization_slug": "org"})
    assert resp.status_code == 302
    assert resp["location"] == finish_url
    resp = client.get(finish_url)
    if idp_initiated and advanced.get("reject_idp_initiated_sso", True):
        assert "socialaccount/authentication_error.html" in (
            t.name for t in resp.templates
        )
    else:
        assert resp["location"] == expected_url
        account = SocialAccount.objects.get(
            provider="urn:dev-123.us.auth0.com", uid="dummysamluid"
        )
        assert account.extra_data["Role"] == ["view-profile", "manage-account-links"]
        email = EmailAddress.objects.get(user=account.user)
        assert email.email == (user.email if is_connect else "john.doe@email.org")


def test_acs_error(client, db, saml_settings):
    data = {"SAMLResponse": "bad-response"}
    resp = client.post(
        reverse("saml_acs", kwargs={"organization_slug": "org"}), data=data
    )
    assert resp.status_code == 302
    resp = client.get(resp["location"])
    assert "socialaccount/authentication_error.html" in (t.name for t in resp.templates)


def test_acs_get(client, db, saml_settings):
    """WHile ACS expects POST, it always redirects and handles the request in
    the FinishACSView.
    """
    resp = client.get(reverse("saml_acs", kwargs={"organization_slug": "org"}))
    assert resp.status_code == 302
    resp = client.get(resp["location"])
    assert "socialaccount/authentication_error.html" in (t.name for t in resp.templates)


def test_sls_get(client, db, saml_settings):
    """SLS expects POST"""
    resp = client.get(reverse("saml_sls", kwargs={"organization_slug": "org"}))
    assert resp.status_code == 400


def test_login_on_get(client, db, saml_settings):
    resp = client.get(reverse("saml_login", kwargs={"organization_slug": "org"}))
    assert resp.status_code == 200
    assertTemplateUsed(resp, "socialaccount/login.html")


def test_login(client, db, saml_settings):
    resp = client.post(
        reverse("saml_login", kwargs={"organization_slug": "org"})
        + "?process=connect&next=/foo"
    )
    assert resp.status_code == 302
    location = resp["location"]
    assert location.startswith("https://dev-123.us.auth0.com/samlp/456?SAMLRequest=")
    resp_query = parse_qs(urlparse(location).query)
    # We're not using RelayState
    assert resp_query.get("RelayState") is None
    # We're using the request ID / InResponseTo for tracking state.
    state_id = list(client.session[statekit.STATES_SESSION_KEY].keys())[0]
    assert state_id.startswith("ONELOGIN_")
    state = client.session[statekit.STATES_SESSION_KEY][state_id][0]
    assert state == {"process": "connect", "data": None, "next": "/foo"}


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
        {
            "idp": {
                "entity_id": "dummy",
                "metadata_url": "https://idp.org/sso/",
            },
            "sp": {"entity_id": "dummy-sp-entity-id"},
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
    metadata_url = request.build_absolute_uri(reverse("saml_metadata", args=["org"]))
    sp_entity_id = provider_config.get("sp", {}).get("entity_id")
    if sp_entity_id:
        assert config["sp"]["entityId"] == sp_entity_id
    else:
        assert config["sp"]["entityId"] == metadata_url


@pytest.mark.parametrize(
    "data, result, uid",
    [
        (
            {"urn:oasis:names:tc:SAML:attribute:subject-id": ["123"]},
            {"uid": "123", "email": "nameid@saml.org"},
            "123",
        ),
        ({}, {"email": "nameid@saml.org"}, "nameid@saml.org"),
    ],
)
def test_extract_attributes(db, data, result, uid, settings):
    settings.SOCIALACCOUNT_PROVIDERS = {
        "saml": {
            "APPS": [
                {
                    "client_id": "org",
                    "provider_id": "urn:dev-123.us.auth0.com",
                }
            ]
        }
    }
    provider = get_adapter().get_provider(request=None, provider="saml")
    onelogin_data = Mock()
    onelogin_data.get_attributes.return_value = data
    onelogin_data.get_nameid.return_value = "nameid@saml.org"
    onelogin_data.get_nameid_format.return_value = (
        "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    )
    assert provider._extract(onelogin_data) == result
    assert provider.extract_uid(onelogin_data) == uid
