import json

from django.http import HttpRequest

import pytest

from allauth.core.internal import httpkit


@pytest.mark.parametrize(
    "url,params,expected_url",
    [
        ("/", {"foo": "bar", "v": 1}, "/?foo=bar&v=1"),
        (
            "https://fqdn/?replace=this",
            {"replace": "that"},
            "https://fqdn/?replace=that",
        ),
    ],
)
def test_add_query_params(url, params, expected_url):
    assert httpkit.add_query_params(url, params) == expected_url


@pytest.mark.parametrize(
    "url_template,kwargs,expected_url",
    [
        ("/foo", {}, "http://testserver/foo"),
        ("/foo?key={key}", {"key": " "}, "http://testserver/foo?key=+"),
        ("/foo/{key}", {"key": " "}, "http://testserver/foo/%20"),
        ("https://abs.org/foo?key={key}", {"key": " "}, "https://abs.org/foo?key=+"),
    ],
)
def test_render_url(url_template, kwargs, expected_url, rf):
    request = rf.get("/")
    assert httpkit.render_url(request, url_template, **kwargs) == expected_url


def test_deserialize_request(rf):
    request = rf.get("/")
    assert not request.is_secure()
    serialized = httpkit.serialize_request(request)
    assert not httpkit.deserialize_request(serialized, HttpRequest()).is_secure()
    data = json.loads(serialized)
    data["scheme"] = "https"
    assert httpkit.deserialize_request(json.dumps(data), HttpRequest()).is_secure()
