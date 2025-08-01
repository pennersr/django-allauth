from http import HTTPStatus

from django.urls import reverse


def test_resource(db, client, access_token_generator, user, oidc_client):
    token, _ = access_token_generator(
        client=oidc_client, user=user, scopes=["view-resource"]
    )
    resp = client.get(
        reverse("idp_rest_framework_resource"), HTTP_AUTHORIZATION=f"bearer {token}"
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["user_email"] == user.email


def test_resource_forbidden(db, client, access_token_generator, user, oidc_client):
    token, _ = access_token_generator(
        client=oidc_client, user=user, scopes=["other-resource"]
    )
    resp = client.get(
        reverse("idp_rest_framework_resource"), HTTP_AUTHORIZATION=f"bearer {token}"
    )
    assert resp.status_code == HTTPStatus.FORBIDDEN
