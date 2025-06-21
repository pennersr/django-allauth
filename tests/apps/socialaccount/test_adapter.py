from urllib.parse import parse_qs, urlparse

from django.contrib.sites.models import Site
from django.urls import reverse

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.models import SocialApp


class PrefixStateSocialAccountAdapter(DefaultSocialAccountAdapter):
    def generate_state_param(self, state: dict) -> str:
        return f"prefix-{super().generate_state_param(state)}"


def test_generate_state_param(settings, client, db, google_provider_settings):
    settings.SOCIALACCOUNT_ADAPTER = (
        "tests.apps.socialaccount.test_adapter.PrefixStateSocialAccountAdapter"
    )
    resp = client.post(reverse("google_login"))
    parsed = urlparse(resp["location"])
    query = parse_qs(parsed.query)
    state = query["state"][0]
    assert len(state) == len("prefix-") + statekit.STATE_ID_LENGTH
    assert state.startswith("prefix-")


def test_list_db_based_apps(db, settings):
    app = SocialApp.objects.create(
        provider="saml", provider_id="urn:idp-identity-id", client_id="org-slug"
    )
    app.sites.add(Site.objects.get_current())
    apps = get_adapter().list_apps(None, provider="saml", client_id="org-slug")
    assert app.pk in [a.pk for a in apps]


def test_list_settings_based_apps(db, settings):
    settings.SOCIALACCOUNT_PROVIDERS = {
        "saml": {
            "APPS": [
                {
                    "provider_id": "urn:idp-entity-id",
                    "client_id": "org-slug",
                }
            ]
        }
    }
    apps = get_adapter().list_apps(None, provider="saml", client_id="org-slug")
    assert len(apps) == 1
    app = apps[0]
    assert not app.pk
    assert app.client_id == "org-slug"


def test_get_signup_form_initial_data(sociallogin_factory):
    sociallogin = sociallogin_factory(email="a@b.com")
    # it should pick up sociallogin.email_addresses
    sociallogin.user.email = ""
    initial_data = get_adapter().get_signup_form_initial_data(sociallogin)
    assert initial_data["email"] == "a@b.com"
