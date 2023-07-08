from django.urls import reverse

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
        provider="urn:dev-123.us.auth0.com", uid="dummysamluid@urn:dev-123.us.auth0.com"
    )

    email = EmailAddress.objects.get(user=account.user)
    assert email.email == "john.doe@email.org"
