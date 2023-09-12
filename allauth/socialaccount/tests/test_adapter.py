from django.contrib.sites.models import Site

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialApp


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
