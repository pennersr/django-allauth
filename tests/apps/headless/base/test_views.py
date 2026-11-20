import json
from http import HTTPStatus
from unittest.mock import patch

import pytest


def test_config(db, client, headless_reverse):
    resp = client.get(headless_reverse("headless:config"))
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert set(data["data"].keys()) == {
        "account",
        "mfa",
        "socialaccount",
        "usersessions",
    }


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        '"a string"',
        "123",
        "true",
        "null",
    ],
)
def test_non_object_json_payload(db, client, headless_reverse, payload):
    resp = client.post(
        headless_reverse("headless:account:login"),
        data=payload,
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_malformed_json_payload(db, client, headless_reverse):
    resp = client.post(
        headless_reverse("headless:account:login"),
        data="{not json",
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_too_deeply_nested_json_payload(db, client, headless_reverse):
    # json raises RecursionError when the nesting is too deep for the
    # interpreter's recursion limit, which depends on the Python build and the
    # stack size, so the error is mocked rather than provoked.
    with patch.object(json, "loads", side_effect=RecursionError):
        resp = client.post(
            headless_reverse("headless:account:login"),
            data="[[[]]]",
            content_type="application/json",
        )
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_object_json_payload(db, client, headless_reverse):
    resp = client.post(
        headless_reverse("headless:account:login"),
        data=json.dumps({}),
        content_type="application/json",
    )
    # Empty object is properly validated...
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()["errors"][0]["code"] == "required"
