from pytest_django.asserts import assertTemplateUsed

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base.constants import AuthProcess


def test_bad_redirect(client, headless_reverse, db):
    resp = client.post(
        headless_reverse("headless:socialaccount:redirect_to_provider"),
        data={
            "provider": "dummy",
            "callback_url": "https://unsafe.org/hack",
            "process": AuthProcess.LOGIN,
        },
    )
    assertTemplateUsed(resp, "socialaccount/authentication_error.html")


def test_valid_redirect(client, headless_reverse, db):
    resp = client.post(
        headless_reverse("headless:socialaccount:redirect_to_provider"),
        data={
            "provider": "dummy",
            "callback_url": "/",
            "process": AuthProcess.LOGIN,
        },
    )
    assert resp.status_code == 302


def test_manage_providers(auth_client, user, headless_reverse, provider_id):
    account_to_del = SocialAccount.objects.create(
        user=user, provider=provider_id, uid="p123"
    )
    account_to_keep = SocialAccount.objects.create(
        user=user, provider=provider_id, uid="p456"
    )
    resp = auth_client.get(
        headless_reverse("headless:socialaccount:manage_providers"),
    )
    data = resp.json()
    assert data["status"] == 200
    assert len(data["data"]) == 2
    resp = auth_client.delete(
        headless_reverse("headless:socialaccount:manage_providers"),
        data={"provider": account_to_del.provider, "account": account_to_del.uid},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "status": 200,
        "data": [
            {
                "display": "Unittest Server",
                "provider": {
                    "client_id": "Unittest client_id",
                    "flows": ["provider_redirect"],
                    "id": provider_id,
                    "name": "Unittest Server",
                },
                "uid": "p456",
            }
        ],
    }
    assert not SocialAccount.objects.filter(pk=account_to_del.pk).exists()
    assert SocialAccount.objects.filter(pk=account_to_keep.pk).exists()


def test_disconnect_bad_request(auth_client, user, headless_reverse, provider_id):
    resp = auth_client.delete(
        headless_reverse("headless:socialaccount:manage_providers"),
        data={"provider": provider_id, "account": "unknown"},
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [{"code": "account_not_found", "message": "Unknown account."}],
    }
