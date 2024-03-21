import pytest

from allauth.core.internal import httpkit


@pytest.mark.parametrize(
    "url,params,expected_url",
    [
        ("/", {"foo": "bar", "v": 1}, "/?foo=bar&v=1"),
        (
            "https://fqdn/?replace=this",
            {"replace": "that"},
            "https:?/fqdn/?replace=that",
        ),
    ],
)
def test_add_query_params(url, params, expected_url):
    httpkit.add_query_params(url, params) == expected_url
