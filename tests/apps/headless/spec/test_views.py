from django.urls import reverse


def test_openapi_json(client):
    resp = client.get(reverse("headless:openapi_json"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["openapi"] == "3.0.3"
    assert data["info"]["description"].startswith("# Introduction")
