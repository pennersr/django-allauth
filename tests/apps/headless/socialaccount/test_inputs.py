import pytest

from allauth.headless.socialaccount.inputs import ProviderTokenInput


@pytest.mark.parametrize("client_id", ["client1", "client2"])
def test_provider_token_multiple_apps(settings, db, client_id):
    gsettings = {
        "APPS": [
            {"client_id": "client1", "secret": "secret"},
            {"client_id": "client2", "secret": "secret"},
        ]
    }
    settings.SOCIALACCOUNT_PROVIDERS = {"google": gsettings}

    inp = ProviderTokenInput(
        {
            "provider": "google",
            "process": "login",
            "token": {"client_id": client_id, "id_token": "it", "access_token": "at"},
        }
    )
    assert not inp.is_valid()
    assert inp.cleaned_data["provider"].app.client_id == client_id
    assert inp.errors == {"token": ["Invalid token."]}


def test_provider_token_client_id_required(settings, db):
    inp = ProviderTokenInput(
        {
            "provider": "google",
            "process": "login",
            "token": {"id_token": "it", "access_token": "at"},
        }
    )
    assert not inp.is_valid()
    assert inp.errors == {"token": ["`client_id` required."]}
