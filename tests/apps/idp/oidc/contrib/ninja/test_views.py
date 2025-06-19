from http import HTTPStatus


def test_resource(db, client, access_token_generator, user, oidc_client):
    token, _ = access_token_generator(
        client=oidc_client, user=user, scopes=["view-resource"]
    )
    resp = client.get("/idp/ninja/resource", HTTP_AUTHORIZATION=f"bearer {token}")
    assert resp.status_code == HTTPStatus.OK


def test_resource_forbidden(db, client, access_token_generator, user, oidc_client):
    token, _ = access_token_generator(
        client=oidc_client, user=user, scopes=["other-resource"]
    )
    resp = client.get("/idp/ninja/resource", HTTP_AUTHORIZATION=f"bearer {token}")
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
