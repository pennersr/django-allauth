def test_config(db, client, headless_reverse):
    resp = client.get(headless_reverse("headless:config"))
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["data"].keys()) == {
        "account",
        "mfa",
        "socialaccount",
        "usersessions",
    }
