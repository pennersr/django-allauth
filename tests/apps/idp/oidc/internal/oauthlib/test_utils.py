import pytest

from allauth.idp.oidc.internal.oauthlib.utils import get_uri


@pytest.mark.parametrize(
    "input,output",
    [
        ("/foo?q=param", "/foo?q=param"),
        (
            "/foo?q=a|b&c=c^d&p=`",
            "/foo?q=a%7Cb&c=c%5Ed&p=%60",
        ),
    ],
)
def test_get_uri(rf, input, output):
    request = rf.get(input)
    assert get_uri(request) == output
