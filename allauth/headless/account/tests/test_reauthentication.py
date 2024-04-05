def test_reauthenticate(
    auth_client, user, user_password, headless_reverse, headless_client
):
    resp = auth_client.get(
        headless_reverse("headless:current_session"),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    method_count = len(data["data"]["methods"])

    resp = auth_client.post(
        headless_reverse("headless:reauthenticate"),
        data={
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = auth_client.get(
        headless_reverse("headless:current_session"),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]["methods"]) == method_count + 1
    last_method = data["data"]["methods"][-1]
    assert last_method["method"] == "password"
