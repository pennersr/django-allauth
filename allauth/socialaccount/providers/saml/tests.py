from unittest.mock import patch

from django.urls import reverse
from django.utils.http import urlencode

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount


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
